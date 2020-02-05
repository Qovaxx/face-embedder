from abc import ABCMeta
from typing import (
	Any,
	TypeVar,
	Dict,
	Tuple
)
import warnings

T = TypeVar("T")


class RegistryMeta(ABCMeta):

	def __new__(mcls, name: str, bases: Tuple[T], namespace: Dict[str, Any], **kwargs) -> T:
		cls = super().__new__(mcls, name, bases, namespace)
		registry = kwargs["registry"]
		if name in registry.module_dict.keys():
			current_class = f"<class '{namespace['__module__']}.{namespace['__qualname__']}'>"
			warnings.warn(
				f"{current_class} redefined name '{name}' that was already registered by {registry.get(name)}")
		if "Converter" in name:
			name = f"{namespace['__module__'].split('.')[-1]}.{name}"
		registry.register_module(name, cls)

		return cls
