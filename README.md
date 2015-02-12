Introduction to Python Gevent
=============================

Epitaph to Threads
------------------
Anyone who has been coding long enough to have a taste of **threading** would have learned how tedious it is. Threads are often inevitable in Python (as well as many other languages) when a process requires waiting, for instance interaction with a webserver in tasks like downloading and uploading resources. Python by itself wasn't built to be asynchronous (although newer versions include built-in [async implementations](https://docs.python.org/3.4/library/asyncore.html)), meaning processes are run one after another. For example, consider this snippet:

```Python

import time

print("Start process")
time.sleep(5)
print("Life goes on")

```
The above code will never print "Life goes on" unless 5 seconds had passed. Can we imagine increasing the wait time to a minute or five minutes? Computer becomes boring in an instant.

In this case, what we would probably do is spawn a new thread to handle the waiting while the program goes on to do some other things behind it. What the computer does in general is swapping the blocking process out of the way and clear the CPU's task force for other tasks. If you have ever used so much RAM on your computer that an alert pops up saying something about swapping memory, that is pretty illustrative to what a thread does (though not exactly the same). Threads make use of computer's multiprocessors by using each one to handle different threads.

Consider the same code using a thread to handle the wait:

```Python

import time
import threading

def wait(t):
    time.sleep(t)
    print("Done waiting")

print("Start process")
threading.Thread(target=wait, args=(5,)).start()
print("Life goes on")

```
This code print "Life goes on" right away after printing "Start process", then after a few seconds "Done waiting" is printed.

What makes threads so cumbersome are, first, each thread posts considerable amount of overhead, and second, multiple threads sharing a same memory can be very unpredictable. Imagine a situation when a global variable is read and modified by several threads in parallel. How can you be sure each thread ends up with the right value in its hand when there are some others messing around with it? Programmers call this situation a **race**.

Consider this trivial code that shows three threads randomly access a global variable:

```Python

import time
import threading
import random

val = 1

def increment():
    global val
    time.sleep(random.randint(1, 3))
    val += 1
    time.sleep(random.randint(1, 3))
    val += 1
    time.sleep(random.randint(1, 5))
    val += 1
    print("Should be 4, but got %d" % val)

def multiply():
    global val
    time.sleep(random.randint(0, 3))
    val *= 2
    print("Should be 2, but got %d" % val)

def decrement():
    global val
    val -= 1
    time.sleep(random.randint(0, 4))
    val -= 1
    print("Should be -1, but got %d" % val)

print("Start")
t1 = threading.Thread(target=increment).start()
t2 = threading.Thread(target=multiply).start()
t3 = threading.Thread(target=decrement).start()
print("Behold...")

# print out
# Start
# Behold...
#
#
# (This part will be random)
# Should be 2, but got 0
# Should be -1, but got 1
# Should be 4, but got 2

```
Imagine that global variable stands for a counter counting threads' operations, or a block of heap memory accessed by a global variable. (Read about stack and heap memories [here](http://gribblelab.org/CBootcamp/7_Memory_Stack_vs_Heap.html)) The latter case is probably one of the issues why threading in memory-allocable languages like C/C++ is very tedious. This shared memory problem introduces a concept of [lock or mutex](https://msdn.microsoft.com/en-us/magazine/cc163744.aspx), which is simply a mechanism to prevent another thread from accessing a memory when a thread hasn't done its business yet.

The Curious Case of Node.js
---------------------------
Everyone probably heard of [Node.js](http://nodejs.org/) (If not, that's too bad for you). Node gets rid of the concept of thread entirely by running an event loop on a single thread polling for events thus creating an illusion of parallelism through concurrency. For network I/O applications, it's proven highly efficient.

[Twisted](https://twistedmatrix.com/trac/) is arguably one of the first successful Python implementation of eventloop-style asynchronosity. It uses a loop called **reactor**, and is event-driven by attaching "future" callable functions to a *Deferred* object which can be called later asynchronously in what is known as a callback chain. In my opinion, Twisted is a very powerful and complete asychronous network toolset, but its legacy origin made it non-conform to many Python PEP standards and its concept of Deferreds can be difficult for modern developers to grasp. Python's current direction toward async is in many ways built with some kind of inspiration from Twisted.

Enter Gevent 
------------
[Gevent](http://www.gevent.org/) is a Python coroutine-based network library (the keyword is "coroutine" instead of "event-driven"). It uses Python [Greenlet](https://greenlet.readthedocs.org/en/latest/), a form of light-weight threads which simplify the problems found in traditional threads and perform data exchanges through "channels." (You can read about How [Go](http://golang.org/) language deals with concurrency using similar coroutines and channels) while exposing event-driven style APIs based on [libev](http://software.schmorp.de/pkg/libev.html). Simply put, Greenlets are light pseudo-threads which run inside a single OS process/thread against actual [POSIX threads](https://computing.llnl.gov/tutorials/pthreads/) which are run in *parallel* outside of the main program. It is important to remember that **only one instance of Greenlet is running at any given time**.

When we talk about Concurrency, what we actually means is breaking a chunk of task into multiple smaller subtasks which can be managed and scheduled to run simultaneously. Greenlets are scheduled *cooperatively*, meaning that a greenlet gives up control when it blocks and switch into running another greenlet. We call this action a *context switch*.

A context switch in gevent is done through *yielding* (as in generators). Take a look at the code below in which two greenlets yield control back and forth to one another when `time.sleep()` blocks. You will have to install `gevent` and `greenlet` with `pip install`.

```Python

import gevent

def foo():
    print('foo is running')
    gevent.sleep(0)
    print('baz is blocking, switch back to foo...DONE!')

def bar():
    gevent.sleep(5)
    print('Finally, bar is DONE!')

def baz():
    print('context switch from foo to bar, still blocking...jump to baz')
    gevent.sleep(1)
    print('visited bar, still blocking, back to baz...DONE!')

fs = [foo, bar, baz]

gevent.joinall([gevent.spawn(f) for f in fs])

```
In the above code, [gevent.joinall()](http://www.gevent.org/gevent.html#gevent.joinall) registers all greenlets and schedule them cooperatively. An optional value can be assigned to a keyword argument *timeout* to signify maximum wait time before timing out. Read each print message to guess the sequence of greenlets run, or run the code yourself. 

Before we go on to the next chapter, I'd like to wrap up the concept of coroutines with a quote from *Go Bootcamp*'s author Matt Aimonetti: 

> ..Do not communicate by sharing memory; instead, share memory by communicating.    
> Matt Aimonetti, *Go Bootcamp* (https://github.com/gobootcamp/book), 71
>

Welcome to Gevent Land.





