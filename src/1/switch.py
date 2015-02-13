#!/usr/bin/python

import gevent

def foo():
    print('foo is running')
    gevent.sleep(0)
    print('baz is blocking, switch back to foo...DONE!')
    print('visiting bar...')

def bar():
    gevent.sleep(5)
    print('Finally, bar is DONE!')

def baz():
    print('context switch from foo to bar, still blocking...jump to baz')
    gevent.sleep(1)
    print('visited bar, still blocking, back to baz...DONE!')
    print('visiting bar again...')

def main():
    fs = [ foo, bar, baz]
    gevent.joinall([gevent.spawn(f) for f in fs])

if __name__ == "__main__":
    main()
