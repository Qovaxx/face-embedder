from typing import (
	NoReturn,
	List
)

import torch
import numpy as np
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score


class AccuracyTopK(object):

	def __init__(self, top_k: int = 1) -> NoReturn:
		self._topk = top_k

	@property
	def topk(self) -> int:
		return self._topk

	@torch.no_grad()
	def __call__(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
		batch_size = target.size(0)
		_, pred = input.topk(self._topk, dim=1, largest=True, sorted=True)
		pred = pred.t()
		correct = pred.eq(target.view(1, -1).expand_as(pred))
		correct_k = correct[:self._topk].view(-1).float().sum(0, keepdim=True)

		return correct_k.mul_(100.0 / batch_size)


class VerificationAccuracy(object):

	def __init__(self, n_folds: int = 10, max_threshold: float = 4) -> NoReturn:
		self._n_folds = n_folds
		self._thresholds = np.arange(0, max_threshold, 0.01)
		self._k_fold = KFold(n_splits=n_folds, shuffle=False)

	def __call__(self, input_batches: List[np.ndarray], target_batches: List[np.ndarray]) -> np.ndarray:
		assert len(input_batches) == len(target_batches), "The number of objects must match in target and input"
		assert len(input_batches[0].shape) == 4,\
			"The input must contain 4 dimensions: (flip axis, pair axis, batch axis, embedding axis)"
		input = np.concatenate(input_batches, axis=2)
		target = np.concatenate(target_batches, axis=0)
		folds = list(self._k_fold.split(X=range(target.shape[0])))
		folds_accuracy = np.empty(shape=(0), dtype=float)

		for flip_axis in range(input.shape[0]):
			pairs = input[flip_axis]
			dists = np.power(np.linalg.norm(pairs[0] - pairs[1], axis=1), 2) # cosine = euclid if normalized

			for train_indices, test_indices in folds:
				estimate_fn = lambda x: self._thresh_accuracy_score(dists[train_indices], target[train_indices], x)
				metrics = list(map(lambda x: estimate_fn(x), self._thresholds))
				best_threshold = self._thresholds[np.argmax(metrics)]
				accuracy = self._thresh_accuracy_score(dists[test_indices], target[test_indices], best_threshold)
				folds_accuracy = np.append(folds_accuracy, accuracy)

		return np.asarray(np.mean(folds_accuracy))

	@staticmethod
	def _thresh_accuracy_score(distances: np.ndarray, target: np.ndarray, threshold: float) -> float:
		predictions = np.less(distances, threshold)
		return accuracy_score(target, predictions)
