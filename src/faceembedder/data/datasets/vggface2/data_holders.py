from typing import ClassVar

from .name import DATASET_NAME
from ...base import BaseDataHolder
from ...meta import RegistryMeta
from ...registry import DATAHOLDERS_REGISTRY


class VGGFace2OriginDataHolder(BaseDataHolder, metaclass=RegistryMeta, registry=DATAHOLDERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "Origin"

	_expected_num_images: ClassVar[int] = 3311286
	_expected_num_classes: ClassVar[int] = 9131


class VGGFace2InsightFaceDataHolder(BaseDataHolder, metaclass=RegistryMeta, registry=DATAHOLDERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "InsightFace"

	_expected_num_images: ClassVar[int] = 3137807
	_expected_num_classes: ClassVar[int] = 8631
