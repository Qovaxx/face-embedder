from typing import NoReturn

from torch import nn
from typing_extensions import final

from .base import ModelFactory
from .embedders import (
	iresnet34,
	iresnet50,
	iresnet100,
	IResNet
)
from .layers import (
	LinearProduct,
	NormLinearProduct
)
from .utils import partial_class

__all__ = ["LinearModelFactory", "NormLinearModelFactory"]


@final
class LinearModelFactory(ModelFactory):

	def __init__(self, num_classes: int = 1000,
	             bias: bool = True, init_type: str = "insightface") -> NoReturn:
		super(LinearModelFactory, self).__init__(num_classes)
		self.bias = bias
		self.init_type = init_type
		self.product_layer = partial_class(LinearProduct, out_features=num_classes,
		                                   bias=bias, init_type=init_type)

	def create_iresnet34(self, *args, **kwargs) -> IResNet:
		return self._make(iresnet34(*args, **kwargs))

	def create_iresnet50(self, *args, **kwargs) -> IResNet:
		return self._make(iresnet50(*args, **kwargs))

	def create_iresnet100(self, *args, **kwargs) -> IResNet:
		return self._make(iresnet100(*args, **kwargs))


@final
class NormLinearModelFactory(ModelFactory):

	def __init__(self, num_classes: int = 1000,
	             init_type: str = "insightface") -> NoReturn:
		super(NormLinearModelFactory, self).__init__(num_classes)
		self.init_type = init_type
		self.product_layer = partial_class(NormLinearProduct,
		                                   out_features=num_classes, init_type=init_type)

	def create_iresnet34(self, *args, **kwargs) -> IResNet:
		return self._make(iresnet34(*args, **kwargs))

	def create_iresnet50(self, *args, **kwargs) -> IResNet:
		return self._make(iresnet50(*args, **kwargs))

	def create_iresnet100(self, *args, **kwargs) -> IResNet:
		return self._make(iresnet100(*args, **kwargs))
