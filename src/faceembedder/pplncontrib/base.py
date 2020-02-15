from typing import (
	Callable,
	NoReturn,
	List,
	TypeVar,
	Optional,
	Union
)

import numpy as np
import torch
from torch import nn
from torch.optim.lr_scheduler import _LRScheduler
from torch.optim.optimizer import Optimizer
from torch.utils.data.distributed import DistributedSampler
from torch.utils.data import (
	Sampler,
	RandomSampler,
	SequentialSampler,
	Dataset,
	DataLoader
)
from ppln.data.transforms import make_albumentations
from ppln.utils.misc import (
	cached_property,
	get_dist_info
)
from ppln.utils.config import (
	Config,
	ConfigDict
)
from ppln.hooks.base import BaseHook
from ppln.hooks.registry import HOOKS
from ppln.hooks import (
	DistSamplerSeedHook,
	IterTimerHook,
	LogBufferHook
)
from ppln.runner import Runner
from ppln.hooks.priority import Priority
from ppln.factory import make_model

T = TypeVar("T")


class BaseExperiment(object):

	def __init__(self, config: Config, is_distributed: bool) -> NoReturn:
		self._config = config
		self._is_distributed = is_distributed

		if not is_distributed:
			gpu_count = torch.cuda.device_count()
			config.DATA_LOADER.batch_per_gpu *= gpu_count
			config.DATA_LOADER.workers_per_gpu *= gpu_count

	@property
	def config(self) -> Config:
		return self._config

	@property
	def is_distributed(self) -> bool:
		return self._is_distributed

	@cached_property
	def optimizers(self) -> Optimizer:
		raise NotImplementedError

	@property
	def schedulers(self) -> _LRScheduler:
		raise NotImplementedError

	def dataset(self, mode: str) -> Dataset:
		raise NotImplementedError

	def dp_sampler(self, mode: str, dataset: Dataset) -> Sampler:
		if "train" in mode:
			# from torch.utils.data import WeightedRandomSampler
			# import numpy as np
			# return WeightedRandomSampler(np.ones(len(dataset)), 1000)
			return RandomSampler(dataset, replacement=False)
		else:
			return SequentialSampler(dataset)

	def ddp_sampler(self, mode: str, dataset: Dataset) -> Sampler:
		rank, world_size = get_dist_info()
		shuffle = True if "train" in mode else False
		return DistributedSampler(dataset, num_replicas=world_size, rank=rank, shuffle=shuffle)

	@cached_property
	def model(self) -> nn.Module:
		return make_model(self.config.MODEL)

	def transform(self, mode: str):
		return make_albumentations(self.config.TRANSFORMS[mode])

	def data_loader(self, mode: str) -> DataLoader:
		dataset = self.dataset(mode)

		if self.is_distributed:
			sampler = self.ddp_sampler(mode, dataset)
		else:
			sampler = self.dp_sampler(mode, dataset)

		if "val" in mode:
			batch_size = int(self.config.DATA_LOADER.batch_per_gpu / 2)
			workers_per_gpu = int(self.config.DATA_LOADER.workers_per_gpu / 2)
		else:
			batch_size = self.config.DATA_LOADER.batch_per_gpu
			workers_per_gpu = self.config.DATA_LOADER.workers_per_gpu

		return DataLoader(
			dataset=dataset,
			sampler=sampler,
			shuffle=False,
			batch_size=batch_size,
			num_workers=workers_per_gpu,
			pin_memory=self.config.DATA_LOADER.pin_memory,
			drop_last=("train" in mode)
		)

	@property
	def hooks(self) -> List[Union[ConfigDict, T]]:
		hooks = self.config.HOOKS
		if self.is_distributed:
			hooks.append(DistSamplerSeedHook())
		return hooks + [IterTimerHook(), LogBufferHook()]

	@property
	def work_dir(self) -> str:
		return self.config.WORK_DIR



@HOOKS.register_module
class BaseValidationMetricHook(BaseHook):

	def __init__(self, metric: Callable[[List[np.ndarray], List[np.ndarray]], np.ndarray],
	             metric_name: str) -> NoReturn:
		self._metric = metric
		self._metric_name = metric_name
		self._prediction_batches: Optional[List[np.ndarray]] = None
		self._target_batches: Optional[List[np.ndarray]] = None

	@property
	def priority(self) -> Priority:
		return Priority.NORMAL

	def after_val_iter(self, runner: Runner) -> NoReturn:
		to_numpy = lambda x: x.cpu().detach().numpy()
		self._prediction_batches.append(to_numpy(runner.outputs["predictions"]))
		self._target_batches.append(to_numpy(runner.outputs["targets"]))

	def before_val_epoch(self, runner: Runner) -> NoReturn:
		self._prediction_batches = list()
		self._target_batches = list()

	def after_val_epoch(self, runner: Runner) -> NoReturn:
		metric = self._metric(self._prediction_batches, self._target_batches)
		runner.log_buffer.output[self._metric_name] = metric.item()
