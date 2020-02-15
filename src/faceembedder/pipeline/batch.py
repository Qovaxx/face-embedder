from typing import (
	Any,
	Dict,
	NoReturn
)

import torch
import torch.nn as nn
import torch.nn.functional as F
from ppln.batch_processor import BaseBatchProcessor
from ppln.utils.misc import object_from_dict
from ppln.utils.config import Config


# TODO: add type hints
class BatchProcessor(BaseBatchProcessor):

	def __init__(self, config: Config) -> NoReturn:
		super(BatchProcessor, self).__init__(config)
		self._loss = object_from_dict(config.loss)
		self._metric = object_from_dict(config.metric)
		self._val_flip = config.val_flip

	def train_step(self, model: nn.Module, batch: Dict[str, torch.Tensor], **kwargs) -> Dict[str, Any]:
		images = batch["image"].cuda()
		target = batch["target"].cuda()
		logits = model(images)

		loss = self._loss(logits, target)
		metric = self._metric(logits, target)

		return dict(
			base_loss=loss,
			values=dict(base_loss=loss.item(), acc=metric.item()),
			num_samples=images.size(0)
		)

	def val_step(self, model: nn.Module, batch: Dict[str, torch.Tensor], **kwargs) -> Dict[str, Any]:
		embedder = model.module.embedder
		images1 = batch["image1"].cuda()
		images2 = batch["image2"].cuda()
		targets = batch["target"].cuda()
		pairs = [images1, images2]
		predictions = list()

		for flip_axis in range(1 + int(self._val_flip)):
			predictions.append(list())
			if flip_axis > 0:
				pairs = list(map(lambda x: x.flip(dims=(3,)), pairs))
			for images in pairs:
				embeddings = F.normalize(embedder(images))
				predictions[flip_axis].append(embeddings)

		predictions = torch.stack([torch.stack(flip) for flip in predictions])
		return dict(
			predictions=predictions,
			targets=targets,
			values=dict(),
			num_samples=images1.size(0)
		)
