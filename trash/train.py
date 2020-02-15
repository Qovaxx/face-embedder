from torch.nn import CrossEntropyLoss
import torch
from src.faceembedder.model.factory import LinearModelFactory, NormLinearModelFactory
from src.faceembedder.pipeline.losses import ArcFaceLoss

# model_cfg = dict(type="src.faceembedder.model.NormLinearModelFactory.create_iresnet50",
#                  self=NormLinearModelFactory(num_classes=13123, init_type="other"))



images = 10
classes = 1405

factory = NormLinearModelFactory(num_classes=classes, init_type="insightface")
model = factory.create_iresnet50()

image = torch.rand(images, 3, 112, 112)
labels = torch.empty(images, dtype=torch.long).random_(classes)
logits = model(image)

res = ArcFaceLoss()(logits, labels)
print(res.detach().cpu().numpy().item())


a = 4