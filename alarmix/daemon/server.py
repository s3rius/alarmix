import json
import socket
import threading
from argparse import Namespace

from loguru import logger

from alarmix.daemon import lock
from alarmix.daemon.alarm_manager import AlarmManager
from alarmix.schema import TimeMessageSocket
from alarmix.utils import remove_if_exists


class ServerThread(threading.Thread):
    def __init__(self, manager: AlarmManager, args: Namespace):
        threading.Thread.__init__(self)
        self.manager = manager
        self.socket = args.socket

    def finalize(self) -> None:
        remove_if_exists(self.socket)

    def run(self) -> None:
        logger.info("Started daemon")
        remove_if_exists(self.socket)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.socket)
        logger.debug(f"Successfully bound {self.socket}")
        while True:
            server.listen(1)
            conn, addr = server.accept()
            msg_str = conn.recv(1024)
            if msg_str:
                params = msg_str.decode("utf-8")
                try:
                    message = TimeMessageSocket(**json.loads(params))
                    lock.acquire()
                    message = self.manager.process_message(message)
                    lock.release()
                    conn.sendall(message.encode("utf-8"))
                except ValueError as err:
                    logger.exception(err)
                    conn.sendall(str(err).encode("utf-8"))
                except Exception as ex:
                    logger.exception(ex)
                    conn.sendall(str(ex).encode("utf-8"))
                conn.close()
