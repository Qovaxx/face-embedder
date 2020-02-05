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

from .labels import NameMap
from ..utils import read_file
from ...base import (
	BaseConverter,
	BaseWriter
)
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
class OriginConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):
	formats: ClassVar[List[str]] = ["original", "funneled", "deepfunneled"]

	def __init__(self, writer: BaseWriter,
	             format: str = "original",
	             verbose: bool = False) -> NoReturn:
		assert format in self.formats
		super().__init__(writer, verbose)
		self._format = format
		self._name_map = NameMap()
		self._image_paths: Optional[List[Path]] = None

	def execute_from(self, path: str, filepath_template: str = "*/*") -> NoReturn:
		if self._format == "original":
			data_path = Path(path) / "lfw"
		else:
			data_path = Path(path) / f"lfw-{self._format}"

		self._image_paths = [x for x in sorted(data_path.rglob(filepath_template)) if x.is_file()]
		self._process_general_data()
		self._process_pairs(path)
		self._writer.flush()

	def _process_general_data(self) -> NoReturn:
		iter = self._image_paths
		if self._verbose:
			iter = tqdm(iter, total=len(iter), desc="Converted: ")

		for image_path in iter:
			image = load_image(str(image_path))
			label = self._name_map.to_label(self._get_person_name(image_path))
			record = ClassificationRecord(image, label)
			self._writer.put(record)

	def _process_pairs(self, path) -> NoReturn:
		to_key_fn = lambda x: f"{self._get_person_name(x)}-{self._get_person_image_index(x)}"
		key_map = {to_key_fn(path):index for index, path in enumerate(self._image_paths)}
		pairs_data = read_file(str(Path(path) / "pairs.txt"))

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
class InsightFaceConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):

	def __init__(self, writer: BaseWriter, verbose: bool = False) -> NoReturn:
		super().__init__(writer, verbose)
		self._name_map = NameMap()

	def execute_from(self, path: str) -> NoReturn:
		pairs_data = read_file(str(Path(path) / "pairs.txt"))[1:]
		with open(str(Path(path) / "lfw.bin"), "rb") as file_stream:
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
				record = ClassificationRecord(image, label=self._name_map.to_label(name))
				self._writer.put(record)

			record = VerificationRecord(idx_1=image_index, idx_2=image_index+1, label=int(pair_label))
			self._writer.put_pair(record)
			image_index += 2
		self._writer.flush()
