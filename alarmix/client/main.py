import json
import os.path
import socket
from argparse import ArgumentParser, Namespace
from typing import Any, List, Optional

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


def render_table(field_names: List[str], alarms_info_list: List[List[Any]]) -> str:
    table = PrettyTable(field_names=field_names)
    table.add_rows(alarms_info_list)
    return table.get_string()


def render_raw(table_fields: List[str], raw_rows: List[List[Any]]) -> str:
    result_str = "\t".join(table_fields)
    for alarm_info in raw_rows:
        result_str += "\n"
        result_str += "\t".join(map(str, alarm_info))
    return result_str


def print_alarms(
    socket_addr: str,
    full_list: bool,
    show_cancelled: bool,
    list_whens: bool,
    raw_table: bool,
) -> str:
    alarms_list_str = send_message(
        socket_addr=socket_addr, action=RequestAction.list, full_list=full_list
    )
    alarms_list = InfoList(**json.loads(alarms_list_str))
    if len(alarms_list.alarms) == 0:
        return "No alarms found"

    table_fields = ["alarm time", "remaining time"]
    if list_whens:
        table_fields.append("when")
    if show_cancelled:
        table_fields.append("cancelled")
    raw_rows = []
    for alarm in alarms_list.alarms:
        row = [str(alarm.time), alarm.remaining]
        if alarm.canceled and not show_cancelled:
            continue
        if list_whens:
            row.append(alarm.when)
        if show_cancelled:
            row.append(alarm.canceled)
        raw_rows.append(row)

    if raw_table:
        return render_raw(table_fields, raw_rows)
    else:
        return render_table(table_fields, raw_rows)


def parse_args() -> Namespace:
    arg_parse = ArgumentParser(
        description="Alarmd client written to interact with your alarms",
        epilog="By default alarmc will list all scheduled alarms",
    )
    subparsers = arg_parse.add_subparsers(dest="namespace")
    add_parser = subparsers.add_parser("add", help="Add new alarm")
    stop_parser = subparsers.add_parser("stop", help="Stop running alarm")
    delete_parser = subparsers.add_parser("delete", help="Delete alarm from schedule")
    cancel_parser = subparsers.add_parser("cancel", help="Cancel alarm for today")
    arg_parse.add_argument(
        "-f",
        "--full",
        default=False,
        dest="full",
        action="store_true",
        help="Print information about all existing alarms (not for today)",
    )
    arg_parse.add_argument(
        "-c",
        "--cancelled",
        default=False,
        dest="cancelled",
        action="store_true",
        help="Show cancelled alarms for today",
    )
    arg_parse.add_argument(
        "-w",
        "--whens",
        default=False,
        dest="list_whens",
        action="store_true",
        help="Show 'when' column in table",
    )
    arg_parse.add_argument(
        "-r",
        "--raw",
        default=False,
        dest="raw_table",
        action="store_true",
        help="Show raw data, instead of a formatted table",
    )
    for parser in (arg_parse, add_parser, stop_parser, delete_parser, cancel_parser):
        parser.add_argument(
            "-s",
            "--socket",
            type=str,
            default=SOCKET_NAME,
            help="Socket path to communicate with daemon",
        )
    for parser in (add_parser, delete_parser, cancel_parser):
        parser.add_argument(
            "time",
            type=str,
            nargs="*",
            help="List of times in format {hours}:{minutes} separated by spaces",
        )
        parser.add_argument(
            "-W", "--when", default=When.auto, type=When, choices=list(When)
        )
    return arg_parse.parse_args()


def loop_time_action(
    socket_addr: str,
    action: RequestAction,
    time_list: List[str],
    when: When,
    allow_relative: bool = False,
) -> None:
    for time_str in time_list:
        if allow_relative:
            time_str = parse_relative_time(time_str)
        answer = send_message(
            socket_addr=socket_addr,
            action=action,
            time_str=time_str,
            when=when,
        )
        print(answer)


def main() -> None:
    args = parse_args()
    try:
        answer = str()
        if args.namespace is None:
            answer = print_alarms(
                socket_addr=args.socket,
                full_list=args.full,
                show_cancelled=args.cancelled,
                list_whens=args.list_whens,
                raw_table=args.raw_table,
            )
        elif args.namespace == "add":
            loop_time_action(
                socket_addr=args.socket,
                action=RequestAction.add,
                time_list=args.time,
                when=args.when,
                allow_relative=True,
            )
        elif args.namespace == "cancel":
            loop_time_action(
                socket_addr=args.socket,
                action=RequestAction.cancel,
                time_list=args.time,
                when=args.when,
            )
        elif args.namespace == "delete":
            loop_time_action(
                socket_addr=args.socket,
                action=RequestAction.delete,
                time_list=args.time,
                when=args.when,
            )
        elif args.namespace == "stop":
            answer = send_message(socket_addr=args.socket, action=RequestAction.stop)
        print(answer)
    except AlarmDaemonIsNotRunning:
        print("Are you sure that timer daemon is running.")


if __name__ == "__main__":
    main()
