import numpy as np
from tqdm import tqdm
from qiskit import QuantumCircuit
import sys
import pandas as pd
from math import ceil
from fractions import Fraction
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

np.set_printoptions(threshold=sys.maxsize)

def get_coeffs(x, N, n_q, n_count):
    vec = np.zeros(2**n_q)
    base = 1
    for i in range(2**n_count):
        s1 = np.binary_repr(i,n_count)
        mod2 = np.mod(base,N)
        base = mod2*x
        s2 = np.binary_repr(mod2,n_q-n_count) #IMPORTATNT that n_q-n_count must be >= log2(N)
        # print(i,mod2,s1,s2)
        vec[int(s2+s1,2)] = 1
    return vec

def qft_dagger(n):
    """n-qubit QFTdagger the first n qubits in circ"""
    qc = QuantumCircuit(n)
    # Don't forget the Swaps!
    for qubit in range(n//2):
        qc.swap(qubit, n-qubit-1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc

for i in tqdm(range (4,17), "Shit happens"):
    x       = 2
    N       = 55
    n_count = i # number of qubits of QFT_register
    n_q     = ceil(np.log2(N)) + n_count + 1 # total number of Qubits (QFT_register + a**i_register)
    vec     = get_coeffs(x, N, n_q, n_count)
    vec     = np.multiply(vec, 1/np.sqrt(2**n_count))

    Q = QuantumCircuit(n_q,n_count)
    Q.initialize(vec)
    Q.append(qft_dagger(n_count),range(n_count))
    Q.measure(range(n_count),range(n_count))
    Q.draw(fold=-1)  # -1 means 'do not fold'

    aer_sim       = Aer.get_backend('aer_simulator')
    t_qc          = transpile(Q, aer_sim)
    results       = aer_sim.run(t_qc).result()
    counts        = results.get_counts()
    countsDecimal = {Fraction(int(k, 2)/(2**n_count)).limit_denominator(N): v for k, v in counts.items()}

    plot_histogram(counts, title = f"N = {N}; n_count = {n_count}")
    # plt.show()
    plt.savefig(f"../Plots/FractionsPlotN{N}n_count{n_count}.jpg",dpi=300,bbox_inches='tight')

    rows, measured_phases = [], []
    for output in counts:
        decimal = int(output, 2)  # Convert (base 2) string to decimal
        phase = decimal/(2**n_count)  # Find corresponding eigenvalue
        measured_phases.append(phase)
        # Add these values to the rows in our table:
        frac = Fraction(phase).limit_denominator(N)
        # rows.append([f"{output}(bin) = {decimal:>3}(dec)", f"{decimal}/{2**n_count} = {phase:.2f}",f"{frac.numerator}/{frac.denominator}", frac.denominator, np.gcd(x**(frac.denominator//2)-1, N), np.gcd(x**(frac.denominator//2)+1, N)])
        if (np.gcd(x**(frac.denominator//2)-1, N) not in [1,N]) or (np.gcd(x**(frac.denominator//2)+1, N) not in [1,N]): # Getting rid of trivial divisors,
            rows.append([f"{output}(bin) = {decimal:>3}(dec)", f"{frac.numerator}/{frac.denominator}", frac.denominator, np.gcd(x**(frac.denominator//2)-1, N), np.gcd(x**(frac.denominator//2)+1, N)])
    # Print the rows in a table
    # headers=["Register Output", "Phase", "Fraction", "Guess for r", "guess1","guess2"]
    headers = ["Register Output", "Fraction", "Guess for r", "guess1","guess2"]
    df      = pd.DataFrame(rows, columns=headers)

    df.to_csv(f'../Plots/FractionsPlotN{N}n_count{n_count}.csv', index=False)
