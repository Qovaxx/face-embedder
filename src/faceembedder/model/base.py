from abc import (
	abstractmethod,
	ABC
)
from collections import OrderedDict
from typing import (
	NoReturn,
	Optional
)

from torch import nn


class ModelFactory(ABC):

	def __init__(self, num_classes: int) -> NoReturn:
		self.num_classes = num_classes
		self.product_layer: Optional[nn.Module] = None

	def _make(self, embedder: nn.Module) -> nn.Module:
		return nn.Sequential(OrderedDict([
			("embedder", embedder),
			("product_layer", self.product_layer(in_features=embedder.num_features))
		]))

	@abstractmethod
	def create_iresnet34(self, *args, **kwargs) -> nn.Module:
		...

	@abstractmethod
	def create_iresnet50(self, *args, **kwargs) -> nn.Module:
		...

	@abstractmethod
	def create_iresnet100(self, *args, **kwargs) -> nn.Module:
		...
