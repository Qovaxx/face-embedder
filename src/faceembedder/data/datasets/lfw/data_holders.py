from typing import ClassVar

from .name import DATASET_NAME
from ...base import BaseDataHolder
from ...meta import RegistryMeta
from ...registry import DATAHOLDERS_REGISTRY


class LFWOriginDataHolder(BaseDataHolder, metaclass=RegistryMeta, registry=DATAHOLDERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "Origin"

	_expected_num_images: ClassVar[int] = 13233
	_expected_num_classes: ClassVar[int] = 5749
	_expected_num_pairs: ClassVar[int] = 6000


class LFWInsightFaceDataHolder(BaseDataHolder, metaclass=RegistryMeta, registry=DATAHOLDERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "InsightFace"

	_expected_num_images: ClassVar[int] = 12000
	_expected_num_classes: ClassVar[int] = 4281
	_expected_num_pairs: ClassVar[int] = 6000
