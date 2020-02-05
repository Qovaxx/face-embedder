from urllib.request import urlopen
from typing import (
	Dict,
	List,
	NoReturn,
)

from typing_extensions import Final


class NameMap(object):
	LFW_NAMES_URL: Final = "http://vis-www.cs.umass.edu/lfw/lfw-names.txt"

	def __init__(self) -> NoReturn:
		response = urlopen(self.LFW_NAMES_URL)
		names = sorted(map(lambda x: self._extract_name(x), response.readlines()))
		self._map: Dict[str, int] = dict(zip(names, range(len(names))))

	@property
	def names(self) -> List[str]:
		return list(self._map.keys())

	def to_label(self, name: str) -> int:
		return self._map[name]

	def __getitem__(self, name: str) -> int:
		return self.to_label(name)

	def __len__(self) -> int:
		return len(self._map)

	@staticmethod
	def _extract_name(line: bytes) -> str:
		name = line.strip().split()[0]
		return str(name, "utf-8")
