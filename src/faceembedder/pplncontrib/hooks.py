import datetime
from typing import NoReturn

from colorama import (
	Fore,
	Style
)
from ppln.runner import Runner
from ppln.hooks.registry import HOOKS
from ppln.hooks import BaseDistClosureHook
from ppln.hooks.logger.progress_bar import ProgressBarLoggerHook
from ppln.hooks.logger.text import TextLoggerHook
from ppln.utils.misc import master_only
from ppln.hooks.logger.utils import get_lr
from torch.nn.parallel import DataParallel


@HOOKS.register_module
class PytorchDPHook(BaseDistClosureHook):

	def __init__(self, **kwargs) -> NoReturn:
		super(PytorchDPHook, self).__init__(DataParallel, **kwargs)


@HOOKS.register_module
class ModifiedProgressBarHook(ProgressBarLoggerHook):

	@master_only
	def log(self, runner: Runner) -> NoReturn:
		epoch_color = Fore.YELLOW
		mode_color = (Fore.RED, Fore.BLUE)[runner.train_mode]
		text_color = (Fore.CYAN, Fore.GREEN)[runner.train_mode]
		epoch_text = f"{epoch_color}epoch:{Style.RESET_ALL} {runner.epoch + 1:<4}"
		log_items = [(" " * 11, epoch_text)[runner.train_mode], f"{mode_color}{runner.mode:<5}{Style.RESET_ALL}"]
		log_items.append(f"{text_color}global_iter:{Style.RESET_ALL} {runner.iter + 1}")

		for name, lrs in get_lr(runner.optimizers).items():
			log_items.append(f"{text_color}{name}_lr:{Style.RESET_ALL} {', '.join([f'{lr:.3e}' for lr in lrs])}")

		for name, value in runner.log_buffer.output.items():
			value = f"{value:.2f}" if isinstance(value, float) else value
			log_items.append(f'{text_color}{name}:{Style.RESET_ALL} {value}')
		self.bar.update(f"{' | '.join(log_items)}")


@HOOKS.register_module
class ModifiedTextLoggerHook(TextLoggerHook):

	def _log_info(self, log_dict, runner) -> NoReturn:
		if runner.mode == "train":
			global_iter_str = f"global_iter: {runner.iter + 1}, "
			lr_str = "".join(
				[f"{name}_lr: {', '.join([f'{lr:.3e}' for lr in lrs])}, " for name, lrs in log_dict["lr"].items()])
			log_str =\
				f"Epoch [{log_dict['epoch']}][{log_dict['iter']}/{len(runner.data_loader)}]\t{global_iter_str}{lr_str}"

			if "time" in log_dict.keys():
				self.time_sec_tot += (log_dict["time"] * len(runner.data_loader))
				time_sec_avg = self.time_sec_tot / (runner.iter - self.start_iter + 1)
				eta_sec = time_sec_avg * (runner.max_iters - runner.iter - 1)
				eta_str = str(datetime.timedelta(seconds=int(eta_sec)))
				log_str += f"eta: {eta_str}, "
				log_str += f"time: {log_dict['time']:.2f}, data_time: {log_dict['data_time']:.2f}, "
		else:
			log_str = f"Epoch({log_dict['mode']}) [{log_dict['epoch']}][{log_dict['iter']}]\t"

		log_items = list()
		for name, value in log_dict.items():
			if name in ["Epoch", "mode", "iter", "lr", "time", "data_time", "epoch"]:
				continue
			value = f"{value:.2f}" if isinstance(value, float) else value
			log_items.append(f"{name}: {value}")
		log_str += ", ".join(log_items)
		runner.logger.info(log_str)
