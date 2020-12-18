import os
import signal
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Callable, List

from daemonize import Daemonize
from loguru import logger

from alarmix.daemon.alarm_manager import AlarmManager
from alarmix.daemon.buzzer import BuzzerThread
from alarmix.daemon.server import ServerThread
from alarmix.exceptions import SoundFileNotFound
from alarmix.utils import SOCKET_NAME


def parse_args() -> Namespace:
    arg_parse = ArgumentParser()
    sub_parsers = arg_parse.add_subparsers(dest="namespace")
    kill_parser = sub_parsers.add_parser("kill", help="Kill running daemon if any")
    arg_parse.add_argument(
        "--socket", type=str, default=SOCKET_NAME, help="Socket file to listen"
    )
    arg_parse.add_argument(
        "--backup",
        type=str,
        default=f"{Path.home()}/.alarms.pickle",
        help="File where to store all alarms data",
    )
    arg_parse.add_argument(
        "-s",
        "--sound",
        type=str,
        default=f"{Path.home()}/alarm.mp3",
        help="Sound to play when alarm clock fires",
    )
    arg_parse.add_argument(
        "-d",
        "--daemonize",
        dest="daemonize",
        action="store_true",
        help="Run program as a daemon",
    )
    arg_parse.add_argument(
        "--log-file",
        type=str,
        dest="log_file",
        default="/tmp/alarmd.log",
        help="Log file",
    )
    for parser in (arg_parse, kill_parser):
        parser.add_argument(
            "-p",
            "--pid-file",
            type=str,
            dest="pid",
            default="/tmp/alarmd.pid",
            help="Daemon process ID file",
        )
    return arg_parse.parse_args()


def run_threads(args: Namespace) -> None:
    local_manager = AlarmManager(args.backup)
    local_manager.load_alarms()
    server = ServerThread(local_manager, args)
    buzzer = BuzzerThread(local_manager, args)
    try:
        server.daemon = True
        buzzer.daemon = True

        server.start()
        buzzer.start()

        server.join()
        buzzer.join()
    finally:
        server.finalize()
        buzzer.finalize()
        logger.info("Goodbye, cowboy")
        raise


def gracefully_kill_daemon(pid_file: str) -> None:
    if os.path.exists(pid_file):
        with open(pid_file, "r") as f:
            pid = int(f.read())
        print(f"Found pid: {pid}. Killing ...")
        os.kill(pid, signal.SIGTERM)


def start_program(args: Namespace) -> None:
    logger.add(args.log_file, rotation="10 MB")
    try:
        run_threads(args)
    except KeyboardInterrupt:
        print()
        logger.debug("Stopped by keyboard.")
    except SoundFileNotFound as e:
        logger.debug(f"Exception found: {e}")


def privileged_args(args: Namespace) -> Callable[[], List[Namespace]]:
    def return_args() -> List[Namespace]:
        return [args]

    return return_args


def main() -> None:
    args = parse_args()
    if args.namespace == "kill":
        gracefully_kill_daemon(args.pid)
    else:
        if args.daemonize:
            daemon = Daemonize(
                "alarmix-daemon",
                args.pid,
                start_program,
                privileged_action=privileged_args(args),
            )
            daemon.start()
        else:
            start_program(args)


if __name__ == "__main__":
    main()
