Introduction to Gevent
======================

Foreword
--------
I have been studying for an ideal way of writing asynchronous code in Python. Ideal can have different meanings to different people, but for me it boils down to a balance between straightforwardness, simplicity, elegance and power. I have spent a good time exploring [Twisted](https://twistedmatrix.com/trac/ "Twisted"), a very powerful set of networking libraries and was sad to learn how this pioneer is losing its popularity as others (including the core Python development team) create their own modernized solutions instead of building on top of it. It is a shame, but inevitable as the falls of so many great civilizations.

There are so many interesting solutions out there that deal with async in Python. As the web applications become more and more mainstream and internet is becoming as a vital part of our life, people become more interested in solving network I/O issues than ever. Concept of threads are beginning to be questioned. There's obviously a need for a better solution to concurrency.

I started this writing solely as my personal note on learning [gevent](http://www.gevent.org/ "gevent"), a humble coroutine-based solution to Python async. There is of course [Tornado](http://www.tornadoweb.org/en/stable/ "Tornado"), a very powerful, popular and controversial successor of Twisted. However, as [Flask](http://flask.pocoo.org/ "Flask") is a simple alternative to [Django](https://www.djangoproject.com/ "Django"), so is gevent to Tornado. As I started out with a few gevent programs, I became impressed with its simplicity and high level of abstraction. I decided to dedicate this repository to document my own journey down the road.

This documentation is perhaps more suitable for intermediate Pythonistas with little or no experience in async. If there's anything I missed, by all means, please contribute. Learning is so much better with people who are better than you.

###Install###
Most code is compatible with Python 2.7 and Python 3, though I haven't written any test yet (soon). 
If you have never used Python's **virtual environment**, you have missed the best part of coding in Python. Now is a good time to start. Read how to install [virtualenv](https://virtualenv.pypa.io/en/latest/ "virtualenv") globally, or use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/ "virtualenvwrapper") if you prefer. Python 3.4 also comes with its own [venv](https://docs.python.org/3/library/venv.html "venv") module which is useful.

After you have installed a virtual environment and activate it within this project directory (you can tell by a `(yourenvname)` before your terminal prompt), install the required dependencies with `pip install`:
```Shell

pip install -r requirements.txt

```
Note that without a `virtualenv`, the packages will be installed to your OS's Python main site packages directory and will also be likely to work.

###Concurrency and Parallelism###
To get the terminologies out of the way, first let's understand these two synonymous yet different concepts. 

*Concurrency* happens when tasks are scheduled in timely manners such that *while A is doing something, make sure B isn't kept waiting*. Think of a person juggling many balls. It may look like magic, but it is pure coordination. The juggler only catch and throw one ball into the air at any given time. However, due to gravity, no ball spends its time hanging in mid air. Each is constantly moving up and down the same time one of them is touching the juggler's hand. 

Imagine another juggler juggling the balls beside the first one. Now we have two jugglers doing roughly the same thing. Both of them are working in *parallel*. There are actually two instances or processes working separately at the same time. This is *Parallelism*.

A traditional, procedural process is like a person throwing one ball up and grab it on its way down, then repeat it or maybe throw the ball to a wall and grab it when it bounces back after that. That person can get as creative as he wants, but he can't avoid waiting for the ball before doing something else next. If the wall is far away, or he throws too high up the air, he will have to wait longer.

Concurrency can become Parallelism, but it doesn't have to. Watch this famous talk [Concurrency isn't Parallelism](https://vimeo.com/49718712 "Concurrency vs Parallelism") by Rob Pike, the creator of the [Go Language](http://golang.org "Golang"). Trust me, it is invaluable. 

###Epitaph to Threads###
Anyone who has been coding long enough to have a taste of **threading** would have learned how tedious it can be, even for seasoned programmers. Threads are often used when a process requires waiting, for instance an interaction with a webserver (i.e. downloading and uploading files). Python by itself wasn't built to be asynchronous (although newer versions include built-in [async implementations](https://docs.python.org/3.4/library/asyncore.html)), meaning tasks in a Python program are run one after another. For example, consider this snippet:

```Python

import time

print("Start process")
time.sleep(5)
print("Life goes on")

```
The above code will never print "Life goes on" unless 5 seconds had passed. Can we imagine increasing the wait time to a minute or five minutes? Computer becomes boring in an instant.

In this case, what we would probably do is spawn a new thread to handle the waiting while the program goes on to do some other things behind it. What the computer does in general is swapping the blocking process out of the way and clear the CPU's task force for other tasks. If you have ever used so much RAM on your computer that an alert pops up saying something about swapping memory, that is pretty illustrative to what a thread does (though not exactly the same). Threading makes use of computer's multiprocessors by using each one to handle different threads.

Consider the same code using a thread to handle the wait function:

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

What makes threads so cumbersome are, first, each thread posts considerable amount of overhead, and second, multiple threads sharing a same memory can be very unpredictable. Imagine a situation when a global variable is read and modified by several threads in parallel. How can you be sure each thread ends up with the right value when there are some others messing with it in parallel or concurrence? Programmers call this situation a **race**.

Consider this trivial code that shows three threads accessing and modifying a global variable at random times. Note that due to the random wait time, it is possible that the variable can be accessed by two threads at exactly the same time:

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

```

"Behold..." is (likely) printed right after "Start". This is because threads `t1`, `t2` and `t3` are spawned "out" of the main program. You can simply think of them as another separate programs. Then, each thread prints out its result depending on who finishes first. You will find that some (if not all) threads will be unhappy due to its obtaining an unexpected value. This is the result of each thread messing with the global variable behind each other's back. Imagine the global variable `val` standing for a critical counter variable counting threads' operations, or a case of block of [heap memory](http://gribblelab.org/CBootcamp/7_Memory_Stack_vs_Heap.html "stack vs heap") accessed by those threads. The latter case is probably one of the issues why threading in memory-allocable languages like C/C++, which allow interactions with heap memories, is very complex to maintain and debug. This shared memory problem introduces a concept of [lock or mutex](https://msdn.microsoft.com/en-us/magazine/cc163744.aspx "thread locks"), which is simply a mechanism to prevent another thread from accessing a shared memory when a thread hasn't done its business yet.

###The Curious Case of Node.js###
You have probably heard of [Node.js](http://nodejs.org/ "Node.js") (If not, that's too bad for you). Node gets rid of the concept of thread entirely by running an event loop on a single thread polling for events thus creating an illusion of parallelism through concurrency (and probably made "async" and "real-time" mainstream). For network I/O applications, which do not require intensive CPU's task force, it's proven highly efficient.

[Twisted](https://twistedmatrix.com/trac/) is arguably one of the first successful Python implementation of loop-style async. It uses a loop called *reactor*, and is event-driven by attaching a chain of "future" callback functions to a *Deferred* object which can be called later asynchronously. It is a very powerful and complete asychronous network tool set, but its legacy origin made it non-conforming to many of Python's PEP standards and its concept of Deferreds can be difficult for modern developers to grasp.

###Enter Gevent###
[Gevent](http://www.gevent.org/) is a Python coroutine-based network library. It uses [Greenlet](https://greenlet.readthedocs.org/en/latest/), a form of light-weight threads which solve the problems found in traditional threads and perform data exchanges through "channels"(You can read about How [Go](http://golang.org/ "Golang") Language deals with concurrency using similar concept through goroutines and channels). Simply put, Greenlets are light pseudo-threads which run inside a single OS process/thread against actual heavy [POSIX threads](https://computing.llnl.gov/tutorials/pthreads/ "POSIX threads"), which are run in parallel outside of the main program. It is important to remember that **only one instance of Greenlet is running at any given time** (remember the juggler).

When we talk about concurrency, what we actually means is breaking a chunk of task into multiple smaller subtasks which can be managed, shuffled, juggled and scheduled to run simultaneously. Greenlets are scheduled cooperatively, meaning that a greenlet gives up control when it blocks and switch to running another avaible greenlet using a [looping mechanism](http://software.schmorp.de/pkg/libev.html "libev") similar to those mentioned in Node.js and Twisted. We call this action a *context switch*. Unlike Twisted, gevent's event loop is started automatically inside a running greenlet. There's no need to run or start a loop explicitly.

A context switch in gevent is done through *yielding* (as in generators). Take a look at the code below in which three greenlets yield control back and forth to one another when `gevent.sleep()` blocks. You will have to install `gevent` and `greenlet` with `pip install` first.

```Python

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

fs = [foo, bar, baz]

gevent.joinall([gevent.spawn(f) for f in fs])

```
In the above code, [gevent.joinall()](http://www.gevent.org/gevent.html#gevent.joinall) registers all greenlets and schedule them cooperatively. An optional value can be assigned to a keyword argument *timeout* to signify maximum wait time before timing out. Read each print message to guess the sequence of greenlets run, or run the code yourself. The result should remind you of how the juggler juggles the balls.

Also, note that we just called [gevent.sleep()](http://www.gevent.org/gevent.html#gevent.sleep) instead of [time.sleep()](https://docs.python.org/3.4/library/time.html). Gevent's `sleep()` blocks and switches to a **Hub** instance, which is like a temporary HQ for greenlets and make cooperative scheduling possible. Using the standard `time.sleep()` does not yield a context switch. We will later talk about how to monkey patch the functions and classes in standard modules with cooperative features of gevent.

Take a look at another example which use [gevent.select()](http://www.gevent.org/gevent.html#gevent.select) as a blocking mechanism to trigger a context switch:

```Python
import gevent
from gevent import select

def g1():
    print('g1 starts...')
    select.select([], [], [], 5)
    print('g1 is DONE!')
    
def g2():
    print('enters g2 while waiting for g1 polling')
    select.select([], [], [], 1)
    print('g1 was probably not done, so jump to g2 again')
    print('g2 is DONE! Only g1 left.')
    
def g3():
    print('hits another polling, switch from g2 to g3')
    gevent.sleep(1)
    print('g3 is DONE! Visiting g1...')
    
gevent.joinall([
    gevent.spawn(g1),
    gevent.spawn(g2),
    gevent.spawn(g3),
])  
    
```
The example is pretty similar to the last one using [gevent.sleep()](http://www.gevent.org/gevent.html#gevent.sleep) to block. In this case, [gevent.select()](http://www.gevent.org/gevent.html#gevent.select) were used in exactly the same way. Since no file descriptors or socket instances where provided for actual polling, `timeout` was assigned to act like `.sleep()`. At this point, you should be relatively familiar with the juggling. If you have run the above code, you would have noticed that gevent actually kept track of each greenlet's progress and status, which is roughly what the **Hub** mentioned earlier is for. As before, I intentionally print out illustrative messages to help track the cooperation easier.

Before we go on, I'd like to wrap up the concept of coroutines with a quote from *Go Bootcamp*'s author Matt Aimonetti, which holds applicable to gevent greenlets: 

> ..Do not communicate by sharing memory; instead, share memory by communicating.    
> Matt Aimonetti, *Go Bootcamp* (https://github.com/gobootcamp/book), 71
>

Hope you all find this writing useful. It is a journal of my own findings as well as yours.

Welcome to Gevent Land.





