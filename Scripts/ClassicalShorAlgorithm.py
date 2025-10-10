from math import gcd
from math import floor
from random import randint
import time

# n = int(input("Enter de number you want to decompose (make sure it is not a prime number !!!): ",))
n=10883*10867

beginnig = time.perf_counter()
def order(n,m):
    t = 1
    while (pow(m, t, n) != 1):
        t+=1
    return int(t)

while True:
    m = randint(2,n-1)
    t=0
    g = gcd(n,m)
    if g != 1:
        m=g
        t=int(n/g)
        break
    else:
        r = order(n,m)
        if r%2 == 0:
            m = pow(m,int(r/2),n)+1
            g = gcd(n,m)
            if g != 1 and g != n:  #We have to check also that g is not n (trivial factorization)
                m=g
                t=int(n/g)
                break
            m = pow(m,int(r/2),n)-1
            g = gcd(n,m)
            if g != 1 and g != n:
                m=g
                t=int(n/g)
                break

time = time.perf_counter() - beginnig
print(n,"=",m,"*",t)
print(f"It took {time:.1f} seconds")
