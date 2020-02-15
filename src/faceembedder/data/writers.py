from pathlib import Path
from typing import NoReturn

import cv2
import bcolz
import numpy as np
from typing_extensions import final

from .base import BaseWriter
from .meta import RegistryMeta
from .registry import WRITERS_REGISTRY
from .records import ClassificationRecord
from .mixins import (
	BcolzMixin,
	FolderMixin
)


@final
class FolderWriter(BaseWriter, FolderMixin, metaclass=RegistryMeta, registry=WRITERS_REGISTRY):

	def __init__(self, path: str) -> NoReturn:
		super().__init__(path)
		self._attributes = list()
		Path(self.data_path).mkdir(exist_ok=True)

	def put(self, record: ClassificationRecord) -> NoReturn:
		assert record.image.shape[2] == 3, "Picture isn't in RGB format"
		label_path = Path(self.data_path) / str(record.label)
		label_path.mkdir(exist_ok=True)
		image_index = len(list(label_path.iterdir())) + 1
		image_path = label_path / f"{image_index}.jpg"
		rgb_image = cv2.cvtColor(record.image, cv2.COLOR_BGR2RGB)
		cv2.imwrite(str(image_path), rgb_image)

		image_relative_path = str(image_path.relative_to(image_path.parent.parent))
		phase = record.phase.value if record.phase is not None else None
		self._attributes.append((
			record.label, record.name, record.fold, phase, image_relative_path, record.additional))

	def flush(self) -> NoReturn:
		images_count = len(list(Path(self.data_path).rglob("*/*")))
		assert images_count == len(self._attributes), "Dimensions of data and attributes did not match"
		self._save_pickle(self._attributes, self.attributes_path)
		if len(self._pairs) > 0:
			self._save_pickle(self._pairs, self.pairs_path)


@final
class BcolzWriter(BaseWriter, BcolzMixin, metaclass=RegistryMeta, registry=WRITERS_REGISTRY):

	def __init__(self, path: str, **kwargs) -> NoReturn:
		super().__init__(path)
		self._data = None
		self._attributes = list()
		clevel = kwargs.get("clevel", 9)
		cname = kwargs.get("cname", "lz4")
		self._cparams = bcolz.cparams(clevel=clevel, cname=cname)

	def put(self, record: ClassificationRecord) -> NoReturn:
		image = np.expand_dims(record.image, axis=0)
		if self._data is None:
			self._data = bcolz.carray(image, rootdir=self.data_path, cparams=self._cparams, mode="w")
		else:
			self._data.append(image)
		phase = record.phase.value if record.phase is not None else None
		self._attributes.append((record.label, record.name, record.fold, phase, record.additional))

	def flush(self) -> NoReturn:
		assert self._data.shape[0] == len(self._attributes), "Dimensions of data and attributes did not match"
		self._data.flush()
		self._save_pickle(self._attributes, self.attributes_path)
		if self._pairs is not None:
			self._save_pickle(self._pairs, self.pairs_path)
