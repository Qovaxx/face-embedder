from dataclasses import (
	dataclass,
	field
)
from typing import (
	Any,
	Dict,
	Optional
)

import numpy as np

from .enums import Phase


@dataclass
class ClassificationRecord(object):
	image: np.ndarray
	label: int
	name: Optional[str] = field(default=None)
	fold: Optional[int] = field(default=None)
	phase: Optional[Phase] = field(default=None)
	additional: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationRecord(object):
	idx_1: int
	idx_2: int
	label: int
	additional: Dict[str, Any] = field(default_factory=dict)
