from abc import (
	ABC,
	abstractmethod,
)
import pickle
import os
import os.path as osp
from typing import (
	Any,
	NoReturn,
	Optional,
	List,
	Tuple,
	ClassVar,
)

from .records import (
	ClassificationRecord,
	VerificationRecord
)
from .registry import (
	READERS_REGISTRY,
	WRITERS_REGISTRY
)
from .mixins import PathMixin


class BaseWriter(ABC, PathMixin):

	def __init__(self, path: str) -> NoReturn:
		os.makedirs(path, exist_ok=True)
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
		assert osp.exists(path) and len(os.listdir(path)) > 0, "The reading folder ьгые exist and mustn't be empty"
		self._path = path
		self._attributes = list()

		if osp.exists(self.pairs_path):
			self._pairs = self._load_pickle(self.pairs_path)
		else:
			self._pairs = None

	@property
	def path(self) -> str:
		return self._path

	@property
	def attributes(self) -> List[Tuple]:
		return self._attributes

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
	def num_images(self) -> int:
		...

	@property
	@abstractmethod
	def num_classes(self) -> int:
		...


class BaseConverter(ABC):

	def __init__(self, src_path, dst_path: str, writer: str = "FolderWriter",
	             verbose: bool = False) -> NoReturn:
		valid_writers: List[str] = list(WRITERS_REGISTRY.register.keys())
		assert writer in valid_writers, f"Available writers are: {valid_writers}"

		self._src_path = src_path
		self._dst_path = dst_path
		self._writer = WRITERS_REGISTRY.get(writer)(path=dst_path)
		self._verbose = verbose

	@property
	def writer(self) -> BaseWriter:
		return self._writer

	@abstractmethod
	def execute(self) -> NoReturn:
		...


class BaseDataHolder(ABC):
	_expected_num_images: ClassVar[int]
	_expected_num_classes: ClassVar[int]
	_expected_num_pairs: ClassVar[Optional[int]] = None

	def __init__(self, path: str, reader: str = "FolderReader", check_properties: bool = True) -> NoReturn:
		valid_readers: List[str] = list(READERS_REGISTRY.register.keys())
		assert reader in valid_readers, f"Available writers are: {valid_readers}"
		self._reader = READERS_REGISTRY.get(reader)(path)
		self._reader.check_structure()
		if check_properties:
			self._check_properties()

	@property
	def pairs(self) -> Optional[List[VerificationRecord]]:
		return self._reader.pairs

	@property
	def num_images(self) -> int:
		return self._reader.num_images

	@property
	def num_classes(self) -> int:
		return self._reader.num_classes

	def get_records_by_label(self, label: int) -> List[ClassificationRecord]:
		attributes = self._reader.attributes
		indices = [index for index in range(len(attributes)) if attributes[index][0] == label]
		return list(map(lambda x: self.__getitem__(x), indices))

	def __len__(self) -> int:
		return self.num_images

	def __getitem__(self, index: int) -> ClassificationRecord:
		return self._reader.get(index)

	def _check_properties(self) -> NoReturn:
		assert self.num_images == self._expected_num_images, "The number of images doesn't meet the expected"
		assert self.num_classes == self._expected_num_classes, "The number of classes does not meet the expected"
		if self.pairs is not None:
			assert len(self.pairs) == self._expected_num_pairs, "The number of pairs does not meet the expected"
