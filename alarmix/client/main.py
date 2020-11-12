import json
import os.path
import socket
from argparse import ArgumentParser, Namespace
from typing import Optional

from alarmix.exceptions import AlarmDaemonIsNotRunning
from alarmix.schema import RequestAction, TimeMessageClient, When
from alarmix.utils import SOCKET_NAME


def send_message(
    socket_addr: str, time_str: Optional[str], when: str, action: RequestAction
):
    """
    Communicate with alarm server running on socket-file.
    """
    if not os.path.exists(socket_addr):
        raise AlarmDaemonIsNotRunning()
    msg_obj = TimeMessageClient(time=time_str, when=when, action=action)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(socket_addr)
        msg = json.dumps(msg_obj.dict()).encode("utf-8")
        sock.sendall(msg)
        data = sock.recv(1024)
        print(data.decode("utf-8"))


def parse_args() -> Namespace:
    arg_parse = ArgumentParser()
    subparsers = arg_parse.add_subparsers(dest="namespace")
    add_parser = subparsers.add_parser("add")
    stop_parser = subparsers.add_parser("stop")
    for parser in (arg_parse, add_parser, stop_parser):
        parser.add_argument(
            "-s",
            "--socket",
            type=str,
            default=SOCKET_NAME,
            help="Socket path to communicate with daemon",
        )
    add_parser.add_argument(
        "time",
        type=str,
        nargs="*",
        help="List of times in format {hours}:{minutes} separated by spaces",
    )
    add_parser.add_argument(
        "-d",
        "--delete",
        dest="delete",
        action="store_true",
        help="If you want to delete this alarms",
    )
    add_parser.add_argument(
        "-w", "--when", default=When.auto, type=When, choices=list(When)
    )
    add_parser.set_defaults(delete=False)
    return arg_parse.parse_args()


def main():
    args = parse_args()
    try:
        if args.namespace is None:
            send_message(args.socket, None, When.auto, RequestAction.list)
        elif args.namespace == "add":
            for time_str in args.time:
                target_action = RequestAction.add
                if args.delete:
                    target_action = RequestAction.delete
                send_message(args.socket, time_str, args.when, target_action)
        elif args.namespace == "stop":
            send_message(args.socket, None, When.auto, RequestAction.stop)
    except AlarmDaemonIsNotRunning:
        print("Are you sure that timer daemon is running.")


if __name__ == "__main__":
    main()
