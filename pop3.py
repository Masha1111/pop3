import socket
import ssl
import argparse
from parse import *


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", type=str, help="Логин")
    parser.add_argument("-p", type=str, help="Пароль")
    parser.add_argument("-n", type=int, help="Номер")
    return parser.parse_args()


def main(login, password, number):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        ssl_sock = ssl.wrap_socket(sock)
        ssl_sock.settimeout(10)
        ssl_sock.connect(('pop3.mail.ru', 995))
        data = ssl_sock.recv(4096).decode()
        if data[:3] != "+OK":
            sys.exit("Проблема соединения")
        try:
            ssl_sock.send(("USER " + login + "\r\n").encode())
            data = ssl_sock.recv(4096).decode()
            if data[:3] != "+OK":
                sys.exit("Возникла проблема с пользователем")
            ssl_sock.send(("PASS " + password + "\r\n").encode())
            data = ssl_sock.recv(4096).decode()
            if data[:3] != "+OK":
                sys.exit("Проблема с паролем")
        except socket.timeout:
            sys.exit("socket таймаут")
        try:
            ssl_sock.send("STAT\r\n".encode())
            data = ssl_sock.recv(4096).decode()
            if data[:3] != "+OK":
                sys.exit("STAT проблема")
        except socket.timeout:
            sys.exit("STAT таймаут")
        try:
            ssl_sock.send("RETR {}\r\n".format(number).encode())
            data = ssl_sock.recv(1024).decode(errors="ignore")
            message = ""
            while data:
                try:
                    if data.split()[0] != '+OK':
                        message += data
                    data = ssl_sock.recv(4096).decode(errors="ignore")
                except socket.timeout:
                    break
            parse(message)
        except socket.timeout:
            sys.exit("Таймаут в получении письма")
        ssl_sock.send("QUIT\r\n".encode())


if __name__ == '__main__':
    args = get_args()
    main(args.l, args.p, args.n)