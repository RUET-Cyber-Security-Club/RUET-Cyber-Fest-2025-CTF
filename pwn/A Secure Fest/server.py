#!/usr/bin/env python3
import socketserver
import os
import signal

HOST = "0.0.0.0"
PORT = 9001
BINARY_PATH = "./fest"


class ForkingTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class FestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # ForkingMixIn already put us in a child process here.
        # Wire the socket to stdin, stdout, stderr of the process.
        sock = self.request

        # Duplicate socket FD to stdio
        os.dup2(sock.fileno(), 0)  # stdin
        os.dup2(sock.fileno(), 1)  # stdout
        os.dup2(sock.fileno(), 2)  # stderr

        # Exec the challenge binary; no return from here on success
        os.execv(BINARY_PATH, [BINARY_PATH])


def main():
    # Ignore zombie children
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    with ForkingTCPServer((HOST, PORT), FestHandler) as server:
        print(f"[+] Listening on {HOST}:{PORT}, serving {BINARY_PATH}")
        server.serve_forever()


if __name__ == "__main__":
    main()
