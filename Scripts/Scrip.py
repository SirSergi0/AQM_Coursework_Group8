from math import gcd
from math import floor
from random import randint

n = 3451

def order(n,m):
    t = 1
    while (pow(m, t, n) != 1):
        t+=1
    return int(t)

while True:
    m = randint(2,floor(n/7)-1)
    t=0
    g = gcd(n,m)
    if g != 1:
        m=g
        t=int(n/g)
        break
    else:
        r = order(n,m)
        if r%2 == 0:
            m = pow(m,(r/2))+1
 
print(n,"=",m,"*",t)
