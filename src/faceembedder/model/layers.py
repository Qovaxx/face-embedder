import math
from typing import (
	ClassVar,
	NoReturn,
	List
)

import torch
import torch.nn.functional as F
from torch import nn


class LinearProduct(nn.Linear):
	valid_types: ClassVar[List[str]] = ["insightface", "standard"]

	def __init__(self, in_features: int, out_features: int,
	             bias: bool = True, init_type: str = "insightface") -> NoReturn:
		assert init_type in self.valid_types, f"Available weight init types are: {self.valid_types}"
		self.init_type = init_type
		super(LinearProduct, self).__init__(in_features, out_features, bias)

	def reset_parameters(self):
		if self.init_type == "insightface":
			nn.init.normal_(self.weight, mean=0, std=0.01)
		elif self.init_type == "standard":
			nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))

		if self.bias is not None:
			fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
			bound = 1 / math.sqrt(fan_in)
			nn.init.uniform_(self.bias, -bound, bound)


class NormLinearProduct(nn.Module):
	valid_types: ClassVar[List[str]] = ["insightface", "kaggle", "other"]

	def __init__(self, in_features: int, out_features: int, init_type: str = "insightface") -> NoReturn:
		assert init_type in self.valid_types, f"Available weight init types are: {self.valid_types}"
		super(NormLinearProduct, self).__init__()
		self.in_features = in_features
		self.out_features = out_features
		self.init_type = init_type
		self.weight = nn.Parameter(torch.FloatTensor(out_features, in_features))
		self.reset_parameters()

	def reset_parameters(self) -> NoReturn:
		if self.init_type == "insightface":
			nn.init.normal_(self.weight, mean=0, std=0.01)
		elif self.init_type == "kaggle":
			stdv = 1. / math.sqrt(self.weight.size(1))
			self.weight.data.uniform_(-stdv, stdv)
		elif self.init_type == "other":
			nn.init.xavier_uniform_(self.weight)

	def forward(self, input: torch.Tensor) -> torch.Tensor:
		return F.linear(F.normalize(input), F.normalize(self.weight), bias=None)

	def extra_repr(self):
		return f"in_features={self.in_features}, out_features={self.out_features}"
