import threading

class Counter:
    def __init__(self):
        self.value = 0
    def increment(self):
        self.value += 1
    def decrement(self):
        self.value -= 1

class SynchronizedCounter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()
    def increment(self):
        self._lock.acquire()
        self.value += 1
        self._lock.release()
    def decrement(self):
        with self._lock:
            self.value -= 1
        
def inc_10000(c):
    for i in range(10000):
        c.increment()
def dec_10000(c):
    for i in range(10000):
        c.decrement()

if __name__ == '__main__':
    # sequential version
    c = Counter(); inc_10000(c); dec_10000(c)
    print 'Sequential Output', c.value # always 0
    # parallel version
    c = Counter()
    t1 = threading.Thread(target=inc_10000,args=(c,))
    t2 = threading.Thread(target=dec_10000,args=(c,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print 'Parallel Output:', c.value # Not always 0!
    # Thread Safe Version
    c = SynchronizedCounter()
    t1 = threading.Thread(target=inc_10000,args=(c,))
    t2 = threading.Thread(target=dec_10000,args=(c,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print 'Thread Safe Output:', c.value # Always 0!
