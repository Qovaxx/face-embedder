from typing_extensions import final

from .name import DATASET_NAME
from ...base import BaseConverter
from ...meta import RegistryMeta
from ...registry import CONVERTERS_REGISTRY
from ..utils import execute_insightface


@final
class MS1MV2InsightFaceConverter(BaseConverter, metaclass=RegistryMeta, registry=CONVERTERS_REGISTRY):
	__dataset__ = DATASET_NAME
	__source__ = "InsightFace"

	execute = execute_insightface
