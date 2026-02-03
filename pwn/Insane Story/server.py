#!/usr/bin/env python3
# server.py
# Simple fork-per-connection server that execs a binary per client.
# The binary itself should print the banner (so server does not).

import socket
import os
import sys
import signal

HOST = "0.0.0.0"
PORT = 1576
BINARY = "./story"   # path to your compiled ELF

def reap_children(signum, frame):
    # Reap any finished children to avoid zombies
    try:
        while True:
            pid, _ = os.waitpid(-1, os.WNOHANG)
            if pid <= 0:
                break
    except ChildProcessError:
        pass

def main():
    # Basic checks
    if not os.path.isfile(BINARY) or not os.access(BINARY, os.X_OK):
        print(f"Binary '{BINARY}' not found or not executable. Build it first.", file=sys.stderr)
        sys.exit(1)

    # Setup SIGCHLD handler to reap children
    signal.signal(signal.SIGCHLD, reap_children)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(50)
        print(f"Listening on {HOST}:{PORT}")

        while True:
            try:
                conn, addr = srv.accept()
            except InterruptedError:
                continue
            except Exception as e:
                print(f"Accept failed: {e}", file=sys.stderr)
                continue

            # Fork per connection
            try:
                pid = os.fork()
            except OSError as e:
                print(f"fork() failed: {e}", file=sys.stderr)
                conn.close()
                continue

            if pid == 0:
                # Child: serve the client by duping socket and execing the binary
                try:
                    srv.close()   # child doesn't need listening socket
                    fd = conn.fileno()

                    # Duplicate socket onto stdin/out/err
                    os.dup2(fd, 0)
                    os.dup2(fd, 1)
                    os.dup2(fd, 2)

                    # Close any other fds >= 3 (best-effort)
                    try:
                        maxfd = os.sysconf("SC_OPEN_MAX")
                    except:
                        maxfd = 1024
                    for fd_to_close in range(3, int(maxfd)):
                        try:
                            os.close(fd_to_close)
                        except OSError:
                            pass

                    # Exec the service binary; it will handle interaction and print banner
                    os.execv(BINARY, [BINARY])
                except Exception:
                    # If exec or any step fails, try to notify client, then exit
                    try:
                        conn.sendall(b"\nInternal server error.\n")
                    except Exception:
                        pass
                    os._exit(1)
                # Should not reach here
                os._exit(0)
            else:
                # Parent: close the connection socket (child has a copy) and continue
                conn.close()

if __name__ == "__main__":
    main()
