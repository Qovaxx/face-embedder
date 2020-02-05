from abc import (
	ABC,
	abstractmethod,
)
import pickle
import os.path as osp
from typing import (
	Any,
	NoReturn,
	Optional,
	List,
	ClassVar
)

from .records import (
	ClassificationRecord,
	VerificationRecord
)
from .mixins import PathMixin


class BaseWriter(ABC, PathMixin):

	def __init__(self, path: str) -> NoReturn:
		self._path = path
		self._pairs = list()

	@property
	def path(self) -> str:
		return self._path

	@abstractmethod
	def put(self, record: ClassificationRecord) -> NoReturn:
		...

	def put_pair(self, record: VerificationRecord) -> NoReturn:
		self._pairs.append(record)

	@abstractmethod
	def flush(self) -> NoReturn:
		...

	@staticmethod
	def _save_pickle(data: Any, path: str) -> NoReturn:
		with open(path, "wb") as file_stream:
			pickle.dump(data, file_stream, protocol=pickle.HIGHEST_PROTOCOL)


class BaseReader(ABC, PathMixin):

	def __init__(self, path: str) -> NoReturn:
		self._path = path
		if osp.exists(self.pairs_path):
			self._pairs = self._load_pickle(self.pairs_path)
		else:
			self._pairs = None

	@property
	def path(self) -> str:
		return self._path

	@property
	def pairs(self) -> Optional[List[VerificationRecord]]:
		return self._pairs

	@abstractmethod
	def get(self, index: int) -> ClassificationRecord:
		...

	@staticmethod
	def _load_pickle(path: str) -> Any:
		with open(path, "rb") as file_stream:
			data = pickle.load(file_stream)
		return data

	@property
	@abstractmethod
	def photos(self) -> int:
		...

	@property
	@abstractmethod
	def identities(self) -> int:
		...


class BaseConverter(ABC):

	def __init__(self, writer: BaseWriter, verbose: bool = False) -> NoReturn:
		self._writer = writer
		self._verbose = verbose

	@property
	def writer(self) -> BaseWriter:
		return self._writer

	@abstractmethod
	def execute_from(self, path: str) -> NoReturn:
		...


class BaseDataHolder(ABC):
	expected_photos: ClassVar[int]
	expected_identities: ClassVar[int]

	def __init__(self, reader: BaseReader, check_properties: bool = True) -> NoReturn:
		self._reader = reader
		if check_properties:
			self._check_properties()

	@property
	def reader(self) -> BaseReader:
		return self._reader

	@property
	def pairs(self) -> Optional[List[VerificationRecord]]:
		return self._reader.pairs

	def __len__(self) -> int:
		return self._reader.photos

	def __getitem__(self, index: int) -> ClassificationRecord:
		return self._reader.get(index)

	def _check_properties(self) -> NoReturn:
		assert self._reader.photos == self.expected_photos, "The number of photos does not meet the expected"
		assert self._reader.identities == self.expected_identities, "The number of identities does not meet the expected"
