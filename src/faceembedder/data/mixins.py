import warnings
import os.path as osp

from typing_extensions import ClassVar

from .enums import DataFormat


class FolderMixin(object):
	format: ClassVar[DataFormat] = DataFormat.FOLDER


class BcolzMixin(object):
	format: ClassVar[DataFormat] = DataFormat.BCOLZ


class PathMixin(object):

	@property
	def data_path(self) -> str:
		return osp.join(self._path, "data")

	@property
	def attributes_path(self) -> str:
		return osp.join(self._path, "attributes.pkl")

	@property
	def pairs_path(self) -> str:
		return osp.join(self._path, "pairs.pkl")

	def check_structure(self):
		assert osp.exists(self.data_path) and osp.isdir(self.data_path)
		assert osp.exists(self.attributes_path) and osp.isfile(self.attributes_path)
		if osp.exists(self.pairs_path):
			assert osp.isfile(self.pairs_path)
		else:
			warnings.warn("Pairs file doesn't exist")
