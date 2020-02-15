import itertools
import os.path as osp
from pathlib import Path
from typing import (
	List,
	NoReturn,
	Dict,
	Union
)
from tqdm import tqdm

import pandas as pd
from typing_extensions import final

from .name import DATASET_NAME
from ..utils import (
	read_file,
	execute_insightface
)
from ...base import BaseConverter
from ...enums import Phase
from ...meta import RegistryMeta
from ...registry import CONVERTERS_REGISTRY
from ...records import ClassificationRecord
from ...utils import load_image


@final
class VGGFace2OriginConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "Origin"

	def __init__(self, src_path, dst_path: str, writer: str = "FolderWriter",
	             verbose: bool = False) -> NoReturn:
		super().__init__(src_path, dst_path, writer, verbose)
		self._filepath_template = "*/*.jpg"
		self._num_classes = 9131
		self._num_attributes = 30000

	def execute(self) -> NoReturn:
		self._load_metadata(self._src_path)
		image_paths = sorted(Path(self._src_path).rglob(self._filepath_template))
		iter = image_paths
		if self._verbose:
			iter = tqdm(iter, total=len(iter), desc="Converted: ")

		for image_path in iter:
			image = load_image(str(image_path))
			basename = image_path.parent.stem
			label = int(basename[1:])
			name = self._meta_map[basename]["name"]
			relative_path = str(image_path.relative_to(image_path.parent.parent))
			phase = self._phase_map[relative_path]
			additional = {
				"bbox": self._bbox_map[relative_path],
				"landmarks": self._landmark_map[relative_path],
				"mustaches": self._mustaches_map.get(relative_path, None),
				"hat": self._hats_map.get(relative_path, None),
				"eyeglasses": self._eyeglasses_map.get(relative_path, None),
				"sunglasses": self._sunglasses_map.get(relative_path, None),
				"gender": self._meta_map[basename]["gender"].strip()
			}
			record = ClassificationRecord(image, label, name, phase=phase, additional=additional)
			self._writer.put(record)
		self._writer.flush()

	def _load_metadata(self, path: str) -> NoReturn:
		self._meta_map = self._load_meta_map(osp.join(path, "identity_meta.csv"))
		assert len(self._meta_map) == self._num_classes,\
			"The size of the meta should be equal the number of classes in the dataset"

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
		       len(self._eyeglasses_map) == len(self._sunglasses_map) == self._num_attributes, \
			"The number of meta attributes must match and be equal to 30.000"

	def _load_meta_map(self, path: str) -> Dict[str, Dict[str, Union[str, int]]]:
		data = pd.read_csv(path)
		data = self._dataframe_to_dict(data, key_column="Class_ID", key_postfix="", columns_to_int=False)
		return data

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
		map.update(self._dataframe_to_dict(train, key_column="NAME_ID", key_postfix=".jpg"))
		map.update(self._dataframe_to_dict(test, key_column="NAME_ID", key_postfix=".jpg"))
		return map

	def _load_common_map(self, path: str) -> Dict[str, int]:
		data = read_file(path)
		return {x[0]: int(x[1]) for x in data}

	@staticmethod
	def _dataframe_to_dict(data: pd.DataFrame, key_column: str, key_postfix: str = "",
	                       columns_to_int: bool = True) -> Dict[str, Dict[str, int]]:
		data.columns = [x.lower().strip() for x in data.columns]
		key_column = key_column.lower()
		if columns_to_int:
			column_map = {column: int for column in data.columns if column != key_column}
			data = data.astype(column_map)
		records = data.to_dict(orient="records")
		slice_fn = lambda x: dict(itertools.islice(x.items(), 1, len(data.columns)))
		return {f"{record[key_column]}{key_postfix}": slice_fn(record) for record in records}


@final
class VGGFace2InsightFaceConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "InsightFace"

	execute = execute_insightface
