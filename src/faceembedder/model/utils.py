import functools
from typing import (
	Any,
	Dict,
	Type,
	TypeVar,
	List,
)

T = TypeVar("T")


def partial_class(cls: Type[T], *args: List[Any], **kwargs: Dict[str, Any]) -> T:

	class PartialClass(cls):
		__init__ = functools.partialmethod(cls.__init__, *args, **kwargs)

	return PartialClass
