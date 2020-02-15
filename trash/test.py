import matplotlib.pyplot as plt
import albumentations as A
import torch
import torch.nn.functional as F
from albumentations.pytorch.transforms import ToTensor
import numpy as np
from torch.utils.data import DataLoader
from src.faceembedder.pipeline.dataset import VerificationDataset
from src.faceembedder.data.datasets.lfw import LFWOriginDataHolder
from src.faceembedder.model.embedders import iresnet34, iresnet50, iresnet100
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from torchvision import transforms

# z = dataset[0]
# plt.imshow(z["image1"])
# plt.show()
# plt.figure()
# plt.imshow(z["image2"])
# plt.show()
# print(z["target"])

# 0.9966666666666667
# 0.9968
# 0.9978333333333333

def show_tensor(tensor, index):
	image = tensor[index].cpu(list()).detach().numpy()
	image = np.moveaxis(image, 0, 2)
	plt.figure()
	plt.imshow(image)
	plt.show()


data_holder = LFWOriginDataHolder("/datasets/interim/folder/LFW-InsightFace", reader="FolderReader", check_properties=False)
transform = A.Compose([A.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5 * 256 / 255] * 3), ToTensor()])
dataset = VerificationDataset(data_holder, transform=transform)
model = iresnet34(pretrained=True).eval().cuda()

dataloader = DataLoader(
	dataset=dataset,
	batch_size=10, # 40
	pin_memory=False,
	drop_last=False
)


batches_embeddings = None
batches_targets = None


for index, batch in enumerate(dataloader):
	print(index)
	use_flip = True
	images1 = batch["image1"].cuda()
	images2 = batch["image2"].cuda()
	target = batch["target"].cuda()

	pairs = [images1, images2]
	predictions = list()

	for flip_axis in range(1 + int(use_flip)):
		predictions.append(list())
		if flip_axis > 0:
			pairs = list(map(lambda x: x.flip(dims=(3,)), pairs))
		for images in pairs:
			embeddings = F.normalize(model(images))
			predictions[flip_axis].append(embeddings)

	predictions = torch.stack([torch.stack(flip) for flip in predictions])

	to_numpy = lambda x: x.cpu().detach().numpy()
	if batches_embeddings is None:
		batches_embeddings = to_numpy(predictions)
		batches_targets = to_numpy(target)
	else:
		batches_embeddings = np.append(batches_embeddings, to_numpy(predictions), axis=2)
		batches_targets = np.append(batches_targets, to_numpy(target), axis=0)

	# if index == 9:
	# 	break

from src.faceembedder.pipeline.metrics import VerificationAccuracy

metric = VerificationAccuracy()
acc = metric(batches_embeddings, batches_targets)
print(f"my {acc.item()}")

n_splits = 10
num_pairs = batches_targets.shape[0]
thresholds = np.arange(0, 4, 0.01)
k_fold = KFold(n_splits=n_splits, shuffle=False)
splits = list(k_fold.split(np.arange(num_pairs)))

acc_by_split = list()

for flip_axis in range(batches_embeddings.shape[0]):
	pairs = batches_embeddings[flip_axis]
	diff = np.subtract(pairs[0], pairs[1])
	distances = np.sum(np.square(diff), axis=1)

	for n_split, split in enumerate(splits):
		# print(n_split)
		train_indices = split[0]
		test_indices = split[1]

		acc_by_threshold = list()
		for threshold in thresholds:
			predictions = np.less(distances[train_indices], threshold)
			accuracy = accuracy_score(batches_targets[train_indices], predictions)
			acc_by_threshold.append(accuracy)

		best_threshold_index = np.argmax(acc_by_threshold)

		predictions = np.less(distances[test_indices], thresholds[best_threshold_index])
		split_accuracy = accuracy_score(batches_targets[test_indices], predictions)
		acc_by_split.append(split_accuracy)

ACCURACY = np.mean(acc_by_split)
print(f"copy {ACCURACY}")