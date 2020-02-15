from typing import (
	NoReturn,
	Union
)

from torch.optim.optimizer import Optimizer
from torch.utils.data import Dataset
from torch.optim.lr_scheduler import _LRScheduler
from ppln.utils.config import Config
from ppln.factory import (
	make_optimizer,
	make_scheduler
)
from ppln.utils.misc import (
	cached_property,
	object_from_dict
)

from .dataset import (
	RecognitionDataset,
	VerificationDataset
)
from ..pplncontrib.base import BaseExperiment


class Experiment(BaseExperiment):

	def __init__(self, config: Config, is_distributed: bool) -> NoReturn:
		super(Experiment, self).__init__(config, is_distributed)

	@cached_property
	def optimizers(self) -> Optimizer:
		return make_optimizer(self.model, self.config.OPTIMIZER)

	@property
	def schedulers(self) -> Union[object, _LRScheduler]:
		return make_scheduler(self.optimizers, self.config.SCHEDULER)

	def dataset(self, mode: str) -> Dataset:
		data_holder = object_from_dict(self.config.DATA[mode]["data_holder"])
		if "train" in mode:
			assert data_holder.num_classes == self.config.DATA[mode]["num_classes"]
			return RecognitionDataset(
				data_holder=data_holder,
				transform=self.transform(mode)
			)
		elif "val" in mode:
			return VerificationDataset(
				data_holder=data_holder,
				transform=self.transform(mode)
			)
