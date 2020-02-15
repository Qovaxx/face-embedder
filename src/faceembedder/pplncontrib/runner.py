from typing import (
	Any,
	Dict,
	NoReturn
)

from torch.utils.data import DataLoader
from ppln.runner import Runner


class ModifiedRunner(Runner):

	def run(self, data_loaders: Dict[str, DataLoader], max_epochs: int, **kwargs: Dict[str, Any]) -> NoReturn:
		"""Start running"""
		self.max_epochs = max_epochs

		self.call("before_run")
		for self.epoch in range(self.epoch, max_epochs):
			for mode, self.data_loader in data_loaders.items():
				self._set_mode(mode)
				self.run_mode(**kwargs)
			if self.stop_training:
				break
		self.call("after_run")

	def _set_mode(self, mode: str) -> NoReturn:
		if "train" in mode:
			self.mode = "train"
		elif "val" in mode:
			self.mode = "val"
		else:
			raise ValueError("Only train and val modes are available")
