from typing import (
	TypeVar,
	Type,
	Dict,
	NoReturn,
	Text
)

T = TypeVar("T")
__all__ = ["READERS_REGISTRY", "WRITERS_REGISTRY", "CONVERTERS_REGISTRY", "DATAHOLDERS_REGISTRY"]


class _Registry(object):

	def __init__(self, name: str) -> NoReturn:
		self._name = name
		self._module_dict = dict()

	def __repr__(self) -> Text:
		class_name = self.__class__.__name__
		format_str = f"{class_name}(name={self._name}, items={list(self._module_dict.keys())})"
		return format_str

	@property
	def name(self) -> str:
		return self._name

	@property
	def module_dict(self) -> Dict[str, T]:
		return self._module_dict

	def get(self, key: str) -> T:
		return self._module_dict.get(key, None)

	def __getattr__(self, key: str) -> T:
		return self._module_dict.get(key, None)

	def register_module(self, name: str, cls: Type[T]) -> NoReturn:
		self._module_dict[name] = cls


READERS_REGISTRY = _Registry("Readers")
WRITERS_REGISTRY = _Registry("Writers")
CONVERTERS_REGISTRY = _Registry("Converters")
DATAHOLDERS_REGISTRY = _Registry("Dataholders")
