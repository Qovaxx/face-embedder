from tqdm import tqdm
from typing import (
	ClassVar,
	NoReturn
)

import cv2
from typing_extensions import final

from ..base import (
	BaseConverter,
	BaseDataHolder,
	BaseWriter
)
from ..records import ClassificationRecord
from ..mxnet import (
	load_records,
	unpack_img,
)
from ..meta import RegistryMeta
from ..registry import (
	CONVERTERS_REGISTRY,
	DATAHOLDERS_REGISTRY,
)


class UMDFacesDataHolder(BaseDataHolder, metaclass=RegistryMeta, registry=DATAHOLDERS_REGISTRY):
	expected_photos: ClassVar[int] = 367888
	expected_identities: ClassVar[int] = 8277


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
			record = ClassificationRecord(image, label)
			self._writer.put(record)
		self._writer.flush()
