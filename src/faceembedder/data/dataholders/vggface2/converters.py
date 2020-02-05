import itertools
import os.path as osp
from pathlib import Path
from typing import (
	List,
	NoReturn,
	Dict
)
from tqdm import tqdm

import cv2
import pandas as pd
from typing_extensions import final

from ..utils import read_file
from ...base import (
	BaseConverter,
	BaseWriter
)
from ...mxnet import (
	load_records,
	unpack_img
)
from ...enums import Phase
from ...meta import RegistryMeta
from ...registry import CONVERTERS_REGISTRY
from ...records import ClassificationRecord
from ...utils import load_image


@final
class OriginConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):

	def __init__(self, writer: BaseWriter, verbose: bool = False) -> NoReturn:
		super().__init__(writer, verbose)

	def execute_from(self, path: str, filepath_template: str = "*/*.jpg") -> NoReturn:
		self._load_metadata(path)
		image_paths = sorted(Path(path).rglob(filepath_template))
		iter = image_paths
		if self._verbose:
			iter = tqdm(iter, total=len(iter), desc="Converted: ")

		for image_path in iter:
			image = load_image(str(image_path))
			label = int(image_path.parent.stem[1:])
			relative_path = str(image_path.relative_to(image_path.parent.parent))
			phase = self._phase_map[relative_path]
			additional = {
				"bbox": self._bbox_map[relative_path],
				"landmarks": self._landmark_map[relative_path],
				"mustaches": self._mustaches_map.get(relative_path, None),
				"hat": self._hats_map.get(relative_path, None),
				"eyeglasses": self._eyeglasses_map.get(relative_path, None),
				"sunglasses": self._sunglasses_map.get(relative_path, None),
			}
			record = ClassificationRecord(image, label, phase=phase, additional=additional)
			self._writer.put(record)
		self._writer.flush()

	def _load_metadata(self, path: str) -> NoReturn:
		self._phase_map = self._load_phase_map(path, "train_list.txt", "test_list.txt")
		self._bbox_map = self._load_facial_map(path, "loose_bb_train.csv", "loose_bb_test.csv")
		self._landmark_map = self._load_facial_map(path, "loose_landmark_train.csv", "loose_landmark_test.csv")
		assert len(self._phase_map) == len(self._bbox_map) == len(self._landmark_map), \
			"The number of phases, bounding boxes and landmarks must match and equal the number of images"

		self._mustaches_map = self._load_common_map(osp.join(path, "07-Mustache_or_Beard.txt"))
		self._hats_map = self._load_common_map(osp.join(path, "08-Wearing_Hat.txt"))
		self._eyeglasses_map = self._load_common_map(osp.join(path, "09-Eyeglasses.txt"))
		self._sunglasses_map = self._load_common_map(osp.join(path, "10-Sunglasses.txt"))
		assert len(self._mustaches_map) == len(self._hats_map) == \
		       len(self._eyeglasses_map) == len(self._sunglasses_map) == 30000, \
			"The number of meta attributes must match and be equal to 30.000"

	def _load_phase_map(self, path: str, train_filename: str, test_filename: str) -> Dict[str, Phase]:
		def _to_dict(data: List[List[str]], fill_value: Phase) -> Dict[str, Phase]:
			flatten = list(map(lambda x: x[0], data))
			return dict(zip(flatten, [fill_value] * len(flatten)))

		train = read_file(osp.join(path, train_filename))
		test = read_file(osp.join(path, test_filename))
		split_map = dict()
		split_map.update(_to_dict(train, fill_value=Phase.TRAIN))
		split_map.update(_to_dict(test, fill_value=Phase.TEST))
		return split_map

	def _load_facial_map(self, path: str, train_filename: str, test_filename: str,
	                     subfolder: str = "bb_landmark") -> Dict[str, Dict[str, int]]:
		train = pd.read_csv(osp.join(path, subfolder, train_filename))
		test = pd.read_csv(osp.join(path, subfolder, test_filename))
		map = dict()
		map.update(self._dataframe_to_dict(train))
		map.update(self._dataframe_to_dict(test))
		return map

	def _load_common_map(self, path: str) -> Dict[str, int]:
		data = read_file(path)
		return {x[0]: int(x[1]) for x in data}

	@staticmethod
	def _dataframe_to_dict(data: pd.DataFrame, name_column: str = "name_id") -> Dict[str, Dict[str, int]]:
		data.columns = [x.lower() for x in data.columns]
		column_map = {column: int for column in data.columns if column != name_column}
		data = data.astype(column_map)
		records = data.to_dict(orient="records")
		slice_fn = lambda x: dict(itertools.islice(x.items(), 1, len(data.columns)))
		return {f"{rec[name_column]}.jpg": slice_fn(rec) for rec in records}


@final
class InsightFaceConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):

	def __init__(self, writer: BaseWriter, verbose: bool = False) -> NoReturn:
		super().__init__(writer, verbose)

	def execute_from(self, path: str) -> NoReturn:
		indexed_records = load_records(path)
		iter = range(1, indexed_records.get_max_index())
		if self._verbose:
			iter = tqdm(iter, total=len(iter), desc="Converted: ")

		for index in iter:
			record = indexed_records.read_idx(index)
			header, image = unpack_img(record)
			image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			label = int(header.label)
			record = ClassificationRecord(image, label, phase=Phase.TRAIN)
			self._writer.put(record)
		self._writer.flush()
