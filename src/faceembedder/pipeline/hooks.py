from typing import NoReturn

from ppln.hooks.registry import HOOKS

from .metrics import VerificationAccuracy
from ..pplncontrib.base import BaseValidationMetricHook


@HOOKS.register_module
class ValidationAccuracyHook(BaseValidationMetricHook):

	def __init__(self, metric_name: str, **kwargs) -> NoReturn:
		metric = VerificationAccuracy(**kwargs)
		super(ValidationAccuracyHook, self).__init__(metric, metric_name)
