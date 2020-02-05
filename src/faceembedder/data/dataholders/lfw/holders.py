from typing import ClassVar

from ...base import BaseDataHolder
from ...meta import RegistryMeta
from ...registry import DATAHOLDERS_REGISTRY


class LFWDataHolder(BaseDataHolder, metaclass=RegistryMeta, registry=DATAHOLDERS_REGISTRY):
	expected_photos: ClassVar[int] = 13233
	expected_identities: ClassVar[int] = 5749
