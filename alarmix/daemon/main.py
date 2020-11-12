from argparse import ArgumentParser, Namespace
from pathlib import Path

from loguru import logger

from alarmix.daemon.alarm_manager import AlarmManager
from alarmix.daemon.buzzer import BuzzerThread
from alarmix.daemon.server import ServerThread
from alarmix.exceptions import SoundFileNotFound
from alarmix.utils import SOCKET_NAME


def parse_args() -> Namespace:
    arg_parse = ArgumentParser()
    arg_parse.add_argument("--socket", type=str, default=SOCKET_NAME)
    arg_parse.add_argument(
        "--backup", type=str, default=f"{Path.home()}/.alarms.pickle"
    )
    arg_parse.add_argument("--sound", type=str, default=f"{Path.home()}/alarm.mp3")
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


def main() -> None:
    args = parse_args()
    try:
        run_threads(args)
    except KeyboardInterrupt:
        print()
        logger.debug("Stopped by keyboard.")
    except SoundFileNotFound as e:
        logger.debug(f"Exception found: {e}")


if __name__ == "__main__":
    main()
