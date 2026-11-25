#!/usr/bin/env python3
"""Drive a QEMU VNC guest. Usage:
  drive.py NAME shot OUT.png
  drive.py NAME click X Y
  drive.py NAME type TEXT
  drive.py NAME key KEY
  drive.py NAME wait SECONDS
  drive.py NAME move X Y
"""
import sys, time, hashlib
from vncdotool import api

def display_for(name):
    n = 20 + int(hashlib.md5(name.encode()).hexdigest(), 16) % 60
    return f"localhost::{5900 + n}"

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    name, cmd = sys.argv[1], sys.argv[2]
    c = api.connect(display_for(name), timeout=60)
    try:
        if cmd == "shot":
            c.captureScreen(sys.argv[3])
        elif cmd == "click":
            x, y = int(sys.argv[3]), int(sys.argv[4])
            c.mouseMove(x, y)
            c.mousePress(1)
        elif cmd == "move":
            c.mouseMove(int(sys.argv[3]), int(sys.argv[4]))
        elif cmd == "type":
            for ch in " ".join(sys.argv[3:]):
                c.keyPress(ch)
                time.sleep(0.02)
        elif cmd == "key":
            c.keyPress(" ".join(sys.argv[3:]))
        elif cmd == "wait":
            time.sleep(float(sys.argv[3]))
        else:
            sys.exit("unknown command " + cmd)
    finally:
        c.disconnect()

if __name__ == "__main__":
    main()
