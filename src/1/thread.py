#!/usr/bin/python

import time
import threading

def wait(t):
    time.sleep(t)
    print('Done waiting')

def main():
    print('Start process')
    threading.Thread(target=wait, args=(5,)).start()
    print('Life goes on')

if __name__ == "__main__":
    main()
