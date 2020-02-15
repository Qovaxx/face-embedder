import pickle
from pathlib import Path
from typing import (
	ClassVar,
	NoReturn,
	List,
	Optional,
)
from tqdm import tqdm

import numpy as np
from typing_extensions import final

from .name import DATASET_NAME
from .labels import NameMap
from ..utils import read_file
from ...base import BaseConverter
from ...meta import RegistryMeta
from ...records import (
	ClassificationRecord,
	VerificationRecord
)
from ...registry import CONVERTERS_REGISTRY
from ...utils import (
	load_image,
	extract_image
)


@final
class LFWOriginConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "Origin"
	valid_types: ClassVar[List[str]] = ["original", "funneled", "deepfunneled"]

	def __init__(self, src_path, dst_path: str, writer: str = "FolderWriter",
	              verbose: bool = False, type: str = "original") -> NoReturn:
		super().__init__(src_path, dst_path, writer, verbose)
		assert type in self.valid_types
		self._type = type
		self._name_map = NameMap()
		self._image_paths: Optional[List[Path]] = None
		self._filepath_template = "*/*"

	def execute(self) -> NoReturn:
		if self._type == "original":
			data_path = Path(self._src_path) / "lfw"
		else:
			data_path = Path(self._src_path) / f"lfw-{self._type}"

		self._image_paths = [x for x in sorted(data_path.rglob(self._filepath_template)) if x.is_file()]
		self._process_samples()
		self._process_pairs()
		self._writer.flush()

	def _process_samples(self) -> NoReturn:
		iter = self._image_paths
		if self._verbose:
			iter = tqdm(iter, total=len(iter), desc="Converted: ")

		for image_path in iter:
			image = load_image(str(image_path))
			name = self._get_person_name(image_path)
			label = self._name_map.to_label(name)
			record = ClassificationRecord(image, label, name)
			self._writer.put(record)

	def _process_pairs(self) -> NoReturn:
		to_key_fn = lambda x: f"{self._get_person_name(x)}-{self._get_person_image_index(x)}"
		key_map = {to_key_fn(path):index for index, path in enumerate(self._image_paths)}
		pairs_data = read_file(str(Path(self._src_path) / "pairs.txt"))

		for line in pairs_data[1:]:
			if len(line) == 3:
				image1_index = key_map[f"{line[0]}-{line[1]}"]
				image2_index = key_map[f"{line[0]}-{line[2]}"]
				record = VerificationRecord(image1_index, image2_index, label=1)
			elif len(line) == 4:
				image1_index = key_map[f"{line[0]}-{line[1]}"]
				image2_index = key_map[f"{line[2]}-{line[3]}"]
				record = VerificationRecord(image1_index, image2_index, label=0)
			else:
				raise ValueError("The pairs.txt line must contain 3 or 4 elements")
			self._writer.put_pair(record)

	@staticmethod
	def _get_person_image_index(path: Path) -> int:
		return int(path.stem.split("_")[-1])

	@staticmethod
	def _get_person_name(path: Path) -> str:
		return path.parent.stem


@final
class LFWInsightFaceConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "InsightFace"

	def __init__(self, src_path, dst_path: str, writer: str = "FolderWriter",
	             verbose: bool = False) -> NoReturn:
		super().__init__(src_path, dst_path, writer, verbose)
		self._name_map = NameMap()

	def execute(self) -> NoReturn:
		pairs_data = read_file(str(Path(self._src_path) / "pairs.txt"))[1:]
		with open(str(Path(self._src_path) / "lfw.bin"), "rb") as file_stream:
			byte_images, pair_labels = pickle.load(file_stream, encoding="bytes")
		assert len(byte_images) == len(pair_labels) * 2 == len(pairs_data) * 2

		image_index = 0
		pair_images = np.array_split(byte_images, len(pair_labels))
		iter = list(zip(pair_images, pair_labels, pairs_data))
		if self._verbose:
			iter = tqdm(iter, total=len(iter), desc="Converted: ")

		for i, (images, pair_label, data) in enumerate(iter):
			names = [data[0], data[0]] if len(data) == 3 else [data[0], data[2]]
			for byte_image, name in zip(images, names):
				image = extract_image(byte_image)
				label = self._name_map.to_label(name)
				record = ClassificationRecord(image, label, name)
				self._writer.put(record)

			record = VerificationRecord(idx_1=image_index, idx_2=image_index+1, label=int(pair_label))
			self._writer.put_pair(record)
			image_index += 2
		self._writer.flush()
