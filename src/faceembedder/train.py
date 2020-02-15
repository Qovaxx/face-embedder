import argparse
from typing import NoReturn

from ppln.utils.config import Config
from ppln.utils.misc import init_dist

# TODO: Swap to relative paths
from src.faceembedder.pplncontrib.runner import ModifiedRunner
from src.faceembedder.pipeline.experiment import Experiment
from src.faceembedder.pipeline.batch import BatchProcessor


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser("Process main train arguments")
	parser.add_argument("--config_path", type=str,
	                    help="Path to the config file")
	parser.add_argument("--is_distributed", default=False, action="store_true",
	                    help="Enable distributed mode")
	parser.add_argument("--local_rank", type=int, default=0,
	                    help="The rank of the node for distributed training")
	return parser.parse_args()


def train(config: Config, is_distributed: bool) -> NoReturn:
	experiment = Experiment(config, is_distributed)
	batch_processor = BatchProcessor(config.BATCH_PROCESSOR)

	runner = ModifiedRunner(
		model=experiment.model,
		optimizers=experiment.optimizers,
		schedulers=experiment.schedulers,
		hooks=experiment.hooks,
		work_dir=experiment.work_dir,
		batch_processor=batch_processor,
	)
	runner.run(
		data_loaders={ # TODO: Make it via config
			"train_ms1mv2": experiment.data_loader("train_ms1mv2"),
			"val_lfw": experiment.data_loader("val_lfw")
		},
		max_epochs=config.MAX_EPOCHS
	)


if __name__ == "__main__":
	args = parse_args()
	config = Config.fromfile(args.config_path)

	if args.is_distributed:
		init_dist(**config.DIST_PARAMS)

	train_func = locals()[config.TRAIN_FUNC]
	train_func(config, args.is_distributed)
