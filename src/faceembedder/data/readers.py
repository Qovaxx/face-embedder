import os.path as osp
from typing import NoReturn

import bcolz
from jpeg4py import JPEG
from typing_extensions import final

from .base import BaseReader
from .meta import RegistryMeta
from .registry import READERS_REGISTRY
from .records import ClassificationRecord
from .mixins import (
	BcolzMixin,
	FolderMixin
)


@final
class FolderReader(BaseReader, FolderMixin, metaclass=RegistryMeta, registry=READERS_REGISTRY):

	def __init__(self, path: str) -> NoReturn:
		super().__init__(path)
		self._attributes = self._load_pickle(self.attributes_path)

	def get(self, index: int) -> ClassificationRecord:
		record = self._attributes[index]
		image_path = osp.join(self.data_path, record[3])
		image = JPEG(image_path).decode()
		return ClassificationRecord(
			image=image,
			label=record[0],
			fold=record[1],
			phase=record[2],
			additional=record[4]
		)

	@property
	def photos(self) -> int:
		return len(self._attributes)

	@property
	def identities(self) -> int:
		return len(set(map(lambda x: x[0], self._attributes)))


@final
class BcolzReader(BaseReader, BcolzMixin, metaclass=RegistryMeta, registry=READERS_REGISTRY):

	def __init__(self, path: str) -> NoReturn:
		super().__init__(path)
		self._data = bcolz.open(self.data_path, mode="r")
		self._attributes = self._load_pickle(self.attributes_path)

	def get(self, index: int) -> ClassificationRecord:
		record = self._attributes[index]
		image = self._data[index]
		return ClassificationRecord(
			image=image,
			label=record[0],
			fold=record[1],
			phase=record[2],
			additional=record[3]
		)

	@property
	def photos(self) -> int:
		return len(self._attributes)

	@property
	def identities(self) -> int:
		return len(set(map(lambda x: x[0], self._attributes)))
