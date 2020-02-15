from typing import (
	Dict,
	Optional,
	NoReturn,
	Union
)

import torch
import albumentations as A
from torch.utils.data import Dataset

from ..data.base import BaseDataHolder


class RecognitionDataset(Dataset):
	"""
	Classification of persons into N classes. Used for training
	"""
	def __init__(self, data_holder: BaseDataHolder, transform: Optional[A.Compose] = None) -> NoReturn:
		self._data_holder = data_holder
		self._transform = transform

	def __len__(self) -> int:
		return self._data_holder.num_images

	def __getitem__(self, index: int) -> Dict[str, Union[torch.Tensor, int]]:
		record = self._data_holder[index]
		result = {"image": record.image, "target": record.label}

		if self._transform:
			result = self._transform(**result)

		return result


class VerificationDataset(Dataset):
	"""
	Verification of pairs of persons 1:1. Used for validation
	"""
	def __init__(self, data_holder: BaseDataHolder, transform: Optional[A.Compose] = None) -> NoReturn:
		assert data_holder.pairs is not None, "The data holder should contain a list of verification pairs"
		self._data_holder = data_holder
		self._transform = transform
		self._pairs = data_holder.pairs

	def __len__(self) -> int:
		return len(self._pairs)

	def __getitem__(self, index: int) -> Dict[str, Union[torch.Tensor, int]]:
		record = self._pairs[index]
		image1 = self._data_holder[record.idx_1].image
		image2 = self._data_holder[record.idx_2].image

		if self._transform:
			image1 = self._transform(image=image1)["image"]
			image2 = self._transform(image=image2)["image"]

		return {"image1": image1, "image2": image2, "target": record.label}


class IdentificationDataset(Dataset):
	"""
	Identification of persons in the database 1:N+1. Used for test. One image is taken from the first dataset (probes)
	and added to the second (gallery|distractors)
	"""
	...
