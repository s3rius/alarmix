import json
import os.path
import socket
from argparse import ArgumentParser, Namespace
from typing import Optional

from prettytable import PrettyTable

from alarmix.exceptions import AlarmDaemonIsNotRunning
from alarmix.schema import InfoList, RequestAction, TimeMessageClient, When
from alarmix.utils import SOCKET_NAME, parse_relative_time


def send_message(
    socket_addr: str,
    action: RequestAction,
    when: When = When.auto,
    time_str: Optional[str] = None,
    full_list: bool = False,
) -> str:
    """
    Communicate with alarm server running on socket-file.
    """
    if not os.path.exists(socket_addr):
        raise AlarmDaemonIsNotRunning()
    msg_obj = TimeMessageClient(
        time=time_str, when=when, action=action, full_list=full_list
    )
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(socket_addr)
        msg = msg_obj.json().encode("utf-8")
        sock.sendall(msg)
        data = sock.recv(1024)
        return data.decode("utf-8")


def print_alarms(socket_addr: str, full_list: bool) -> str:
    alarms_list_str = send_message(
        socket_addr=socket_addr, action=RequestAction.list, full_list=full_list
    )
    table = PrettyTable(field_names=["alarm time", "remaining time", "when"])
    alarms_list = InfoList(**json.loads(alarms_list_str))
    if len(alarms_list.alarms) == 0:
        return "No alarms found"
    for alarm in alarms_list.alarms:
        table.add_row([str(alarm.time), alarm.remaining, alarm.when])
    return table.get_string()


def parse_args() -> Namespace:
    arg_parse = ArgumentParser()
    subparsers = arg_parse.add_subparsers(dest="namespace")
    add_parser = subparsers.add_parser("add")
    stop_parser = subparsers.add_parser("stop")
    delete_parser = subparsers.add_parser("delete")
    arg_parse.add_argument(
        "-f",
        "--full",
        default=False,
        dest="full",
        action="store_true",
        help="Print information about all existing alarms",
    )
    for parser in (arg_parse, add_parser, stop_parser, delete_parser):
        parser.add_argument(
            "-s",
            "--socket",
            type=str,
            default=SOCKET_NAME,
            help="Socket path to communicate with daemon",
        )
    for parser in (add_parser, delete_parser):
        parser.add_argument(
            "time",
            type=str,
            nargs="*",
            help="List of times in format {hours}:{minutes} separated by spaces",
        )
        parser.add_argument(
            "-w", "--when", default=When.auto, type=When, choices=list(When)
        )
    return arg_parse.parse_args()


def main() -> None:
    args = parse_args()
    try:
        answer = str()
        if args.namespace is None:
            answer = print_alarms(socket_addr=args.socket, full_list=args.full)
        elif args.namespace == "add":
            for time_str in args.time:
                time_str = parse_relative_time(time_str)
                answer = send_message(
                    socket_addr=args.socket,
                    action=RequestAction.add,
                    time_str=time_str,
                    when=args.when,
                )
        elif args.namespace == "delete":
            for time_str in args.time:
                answer = send_message(
                    socket_addr=args.socket,
                    action=RequestAction.delete,
                    time_str=time_str,
                    when=args.when,
                )
        elif args.namespace == "stop":
            answer = send_message(socket_addr=args.socket, action=RequestAction.stop)
        print(answer)
    except AlarmDaemonIsNotRunning:
        print("Are you sure that timer daemon is running.")


if __name__ == "__main__":
    main()
