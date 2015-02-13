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

def main():    
    print("Start")
    t1 = threading.Thread(target=increment).start()
    t2 = threading.Thread(target=multiply).start()
    t3 = threading.Thread(target=decrement).start()
    print("Behold...")

if __name__ == "__main__":
    main()
