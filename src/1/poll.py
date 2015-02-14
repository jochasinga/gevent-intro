#!/usr/bin/python

import gevent
from gevent import select

def g1():
    print('g1 starts...')
    select.select([], [], [], 5)
    print('g1 is DONE!')

def g2():
    print('enters g2 while waiting for g1 polling')
    select.select([], [], [], 3)
    print('g1 was probably not done, so jump to g2 again')
    print('g2 is DONE! Only g1 left.')
    
def g3():
    print('hits another polling, switch from g2 to g3')
    gevent.sleep(1)
    print('g3 is DONE! Visiting g1...')

def main():
    gs = [g1, g2, g3]
    gevent.joinall([gevent.spawn(g) for g in gs])

if __name__ == "__main__":
    main()
