import math
from typing import NoReturn

import torch
import torch.nn.functional as F
from torch import nn


# TODO: Validate margin argument values
class ArcFaceLoss(nn.Module):

	def __init__(self, margin: float = 0.5, scale: int = 64, easy_margin: bool = False) -> NoReturn:
		super(ArcFaceLoss, self).__init__()
		self.margin = margin
		self.scale = scale
		self.easy_margin = easy_margin

		self._cos_margin = math.cos(self.margin)
		self._sin_margin = math.sin(self.margin)
		self._threshold = torch.as_tensor(math.cos(math.pi - self.margin))
		self._mm = torch.as_tensor(math.sin(math.pi - self.margin) * self.margin)

	def forward(self, input: torch.Tensor, target: torch.Tensor) -> float:
		cosine_logits = input
		sine = torch.sqrt((1.0 - torch.pow(cosine_logits, 2)).clamp(0, 1))
		marginal_cosine = cosine_logits * self._cos_margin - sine * self._sin_margin

		if self.easy_margin:
			marginal_cosine = torch.where(
				cosine_logits > 0, marginal_cosine, cosine_logits)
		else:
			marginal_cosine = torch.where(
				cosine_logits > self._threshold, marginal_cosine, cosine_logits - self._mm)

		one_hot = torch.zeros(cosine_logits.size(), device=input.device)
		one_hot.scatter_(1, target.view(-1, 1).long(), 1)
		marginal_logits = (one_hot * marginal_cosine) + ((1.0 - one_hot) * cosine_logits)
		marginal_logits *= self.scale

		return F.cross_entropy(marginal_logits, target)


class CombinedMarginLoss(nn.Module):

	def __init__(self, sphere_m: float = 1, arc_m: float = 0.3, cosine_m: float = 0.2,
	             scale: int = 64) -> NoReturn:
		super(CombinedMarginLoss, self).__init__()
		self.sphere_m = sphere_m
		self.arc_m = arc_m
		self.cosine_m = cosine_m
		self.scale = scale

	def forward(self, input: torch.Tensor, target: torch.Tensor) -> float:
		cosine_logits = input
		theta = torch.acos(cosine_logits)
		marginal_logits = torch.cos(self.sphere_m * theta + self.arc_m) - self.cosine_m
		marginal_logits *= self.scale

		return F.cross_entropy(marginal_logits, target)
