from typing import ClassVar

from .name import DATASET_NAME
from ...base import BaseDataHolder
from ...meta import RegistryMeta
from ...registry import DATAHOLDERS_REGISTRY


class MS1MV2InsightFaceDataHolder(BaseDataHolder, metaclass=RegistryMeta, registry=DATAHOLDERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "InsightFace"

	_expected_num_images: ClassVar[int] = 5822653
	_expected_num_classes: ClassVar[int] = 85742
