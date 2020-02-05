import os.path as osp

import cv2
import numpy as np


def load_image(path: str) -> np.ndarray:
	if not osp.exists(path):
		raise FileNotFoundError(path)
	image = cv2.imread(path)
	if image is None:
		raise IOError(f"Failed to load image at `{path}`")
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	return image


def extract_image(buffer: bytes, make_color_convertation: bool = True) -> np.ndarray:
	image = cv2.imdecode(np.frombuffer(buffer, np.uint8), -1)
	if make_color_convertation:
		return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	else:
		return image
