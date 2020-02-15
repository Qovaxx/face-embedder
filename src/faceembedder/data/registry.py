from abc import (
	ABC,
	abstractmethod,
)
from collections import defaultdict
from typing import (
	Dict,
	Optional,
	TypeVar,
	Type,
	NoReturn,
	Union,
	Text
)


T = TypeVar("T")
REGISTER_TYPE = Dict[str, T]
__all__ = ["READERS_REGISTRY", "WRITERS_REGISTRY", "DATAHOLDERS_REGISTRY", "CONVERTERS_REGISTRY"]


class _BaseRegistry(ABC):

	def __init__(self, name: str) -> NoReturn:
		self._name = name
		self._register: Optional[Union[REGISTER_TYPE, Dict[str, REGISTER_TYPE]]] = None

	@property
	def name(self) -> str:
		return self._name

	@property
	def register(self) -> Union[REGISTER_TYPE, Dict[str, REGISTER_TYPE]]:
		return self._register

	@abstractmethod
	def add(self, *args, **kwargs) -> NoReturn:
		...

	@abstractmethod
	def get(self, *args, **kwargs) -> T:
		...

	def __repr__(self) -> Text:
		class_name = self.__class__.__name__
		format_str = f"{class_name}(name={self._name}, items={list(self._register.keys())})"
		return format_str


class Registry(_BaseRegistry):

	def __init__(self, name: str) -> NoReturn:
		super(Registry, self).__init__(name)
		self._register = dict()

	def add(self, name: str, cls: Type[T]) -> NoReturn:
		self._register[name] = cls

	def get(self, name: str) -> T:
		return self._register.get(name, None)


class DoubleRegistry(_BaseRegistry):

	def __init__(self, name: str) -> NoReturn:
		super(DoubleRegistry, self).__init__(name)
		self._register = defaultdict(dict)

	def add(self, parent_name: str, child_name: str, cls: Type[T]) -> NoReturn:
		self._register[parent_name][child_name] = cls

	def get(self, parent_name: str, child_name: str) -> T:
		parent = self._register.get(parent_name, None)
		return None if parent is None else parent.get(child_name, None)


READERS_REGISTRY = Registry("Readers")
WRITERS_REGISTRY = Registry("Writers")
DATAHOLDERS_REGISTRY = DoubleRegistry("DataHolders")
CONVERTERS_REGISTRY = DoubleRegistry("Converters")
