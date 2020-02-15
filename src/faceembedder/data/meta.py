from abc import ABCMeta
from typing import (
	Any,
	TypeVar,
	Dict,
	Tuple
)
import warnings

from .registry import (
	Registry,
	DoubleRegistry
)


T = TypeVar("T")


class RegistryMeta(ABCMeta):

	def __new__(mcls, name: str, bases: Tuple[T], namespace: Dict[str, Any], **kwargs) -> T:
		cls = super().__new__(mcls, name, bases, namespace)
		registry = kwargs["registry"]

		if isinstance(registry, Registry):
			if name in registry.register.keys():
				current_class = f"<class '{namespace['__module__']}.{namespace['__qualname__']}'>"
				warnings.warn(
					f"{current_class} redefined name '{name}' that was already registered by {registry.get(name)}")
			registry.add(name, cls)

		elif isinstance(registry, DoubleRegistry):
			assert "__dataset__" in dir(cls) and "__source__" in dir(cls)
			parent_name = cls.__dataset__
			child_name = cls.__source__

			class_name = registry.get(parent_name, child_name)
			if class_name:
				current_class = f"<class '{namespace['__module__']}.{namespace['__qualname__']}'>"
				warnings.warn(
					f"{current_class} redefined name '{parent_name}:{child_name}'"
					f" that was already registered by {class_name}")
			registry.add(parent_name, child_name, cls)

		else:
			raise ValueError("Unknown register type")

		return cls
