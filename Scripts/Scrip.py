from math import gcd
from math import floor
from random import randint

n = int(input("Enter de number you want to decompose (make sure it is not a prime number !!!): ",))
# n=15

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
            if g != 1:
                m=g
                t=int(n/g)
                break
            m = pow(m,int(r/2),n)-1
            g = gcd(n,m)
            if g != 1:
                m=g
                t=int(n/g)
                break
 
print(n,"=",m,"*",t)
