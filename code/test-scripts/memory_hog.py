#!/usr/bin/env python3
import threading
import time

def memory_and_cpu_hog():
    # 1) Allocate ~200 MB
    big = bytearray(30 * 1024 * 1024)
    print("Allocated 30 MB of RAM")

    # 2) Burn CPU in a tight loop
    print("Starting CPU burn—CTRL+C to stop")
    while True:
        # trivial work to keep CPU pegged
        _ = sum(i*i for i in range(1000))

if __name__ == "__main__":
    memory_and_cpu_hog()
