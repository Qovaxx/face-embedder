from typing import ClassVar

from ...base import BaseDataHolder
from ...meta import RegistryMeta
from ...registry import DATAHOLDERS_REGISTRY


class VGGFace2DataHolder(BaseDataHolder, metaclass=RegistryMeta, registry=DATAHOLDERS_REGISTRY):
	expected_photos: ClassVar[int] = 3311286
	expected_identities: ClassVar[int] = 9131
