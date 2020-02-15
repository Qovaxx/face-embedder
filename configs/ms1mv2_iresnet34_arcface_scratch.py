EXPERIMENT_NAME = "ms1mv2_iresnet34_arcface_scratch"
TRAIN_FUNC = "train"


# Data settings
NUM_CLASSES = 85742
DATA_LOADER = dict(
    batch_per_gpu=128,
    workers_per_gpu=5,
    pin_memory=False,
)
DATA = dict(
    train_ms1mv2 = dict(
        data_holder=dict(type="src.faceembedder.data.datasets.ms1mv2.MS1MV2InsightFaceDataHolder",
                         path="/datasets/interim/folder/MS1MV2-InsightFace",
                         reader="FolderReader", check_properties=True),
        num_classes=NUM_CLASSES
    ),
    val_lfw = dict(
        data_holder=dict(type="src.faceembedder.data.datasets.lfw.LFWInsightFaceDataHolder",
                         path="/datasets/interim/folder/LFW-InsightFace",
                         reader="FolderReader", check_properties=True)
    )
)


# Transforms settings
pre_transforms = []
transforms = [
    dict(type="HorizontalFlip", always_apply=False, p=0.5)
]
post_transforms = [
    dict(type="Normalize", mean=[0.5, 0.5, 0.5], std=[0.5 * 256 / 255] * 3,
         max_pixel_value=255.0, always_apply=False, p=1.0),
    dict(type="ToTensor", normalize=None)
]
TRANSFORMS = dict(
    train_ms1mv2=pre_transforms + transforms + post_transforms,
    val_lfw=pre_transforms + post_transforms,
)


# Model settings # TODO: Resume only for embedder
from src.faceembedder.model import NormLinearModelFactory
MODEL = dict(
    type="src.faceembedder.model.NormLinearModelFactory.create_iresnet34",
    self=NormLinearModelFactory(NUM_CLASSES, init_type="insightface"),
    pretrained=False, progress=False
)


# Optimizer settings # TODO: Rescale gradients
OPTIMIZER = dict(type="torch.optim.SGD", lr=0.1,
                 momentum=0.9, weight_decay=0.0005,
                 dampening=0, nesterov=False)
SCHEDULER = dict(type="torch.optim.lr_scheduler.MultiStepLR",
                 last_epoch=-1, gamma=0.1,
                 milestones=[100000, 160000, 180000])
MAX_EPOCHS = 999999


# Batch_processor
LOSS = dict(type="src.faceembedder.pipeline.losses.ArcFaceLoss",
            margin=0.5, scale=64, easy_margin=False)
METRIC = dict(type="src.faceembedder.pipeline.metrics.AccuracyTopK",
              top_k=1)
BATCH_PROCESSOR = dict(loss=LOSS, metric=METRIC, val_flip=True)


# Runtime settings
WORK_DIR = f"/dumps/{EXPERIMENT_NAME}"
DIST_PARAMS = dict(backend="nccl")


# Hook settings
train_metric_name = "acc"
val_metric_name = "val_acc"
HOOKS = [
    dict(type="ModifiedProgressBarHook", bar_width=10),
    dict(type="ModifiedTextLoggerHook"),
    dict(type="CheckpointHook", metric_name=val_metric_name, num_checkpoints=10, mode="max",
         save_optimizer=True, save_scheduler=True),
    dict(type="ValidationAccuracyHook", metric_name=val_metric_name, n_folds=10, max_threshold=4),
    dict(type="LRSchedulerHook", name="base", metric_name=train_metric_name, by_epoch=False),
    dict(type="PytorchDPHook"),
    dict(type="OptimizerHook"),
    # dict(type="PytorchDDPHook"),
    # dict(type="ApexInitializeHook", opt_level='O1'),
    # dict(type="ApexSyncBNHook"),
    # dict(type="ApexDDPHook", delay_allreduce=True),
    # dict(type="ApexOptimizerHook"),
]
