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
from matplotlib.ticker import FuncFormatter
from collections import Counter
import matplot2tikz

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


def to_fraction(x, pos):
    # Convert to a simplified fraction with denominator up to 128
    f = Fraction(x).limit_denominator(128)
    return rf'${f.numerator}/{f.denominator}$' if f.denominator != 1 else rf'${f.numerator}$'

def AnalyticalResult(r,q):
    d = [i for i in range(r)]
    x = np.sort(np.union1d(np.arange(0, q) + 0.01, np.arange(0, ) - 0.01))
    y = np.zeros(len(x))

    for k, i in enumerate(x):
        for j in d[:]:
            y[k] += (np.sin(np.pi * ((j * q) / r - i)) / np.sin(np.pi * (j / r - i / q))) ** 2
        y[k] = y[k] / (r * q ** 2)
    

    for i in range(len(x)): x[i]=x[i]/q
    
    return x,y

for i in tqdm(range (4,17), "Shit happens"):
    x       = 2
    N       = 55
    N_mesurements = 2**14
    r_real  = 20
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
    results       = aer_sim.run(t_qc, shots=N_mesurements).result()
    counts        = results.get_counts()
    for j in range(2 ** n_count):
        key = format(j, f'0{n_count}b') 
        if key not in counts:
            counts[key] = 0
    r_guess = []
    countsNumeric = {int(k, 2)/(2**n_count): v for k, v in counts.items()}
    x_UwU = sorted(countsNumeric.keys())
    y = [countsNumeric[k] for k in x_UwU]
    s = sum(y)
    for k in range(len(y)):
        y[k]= y[k]/s


    # plt.figure(figsize=(10,5))
    plt.bar(x_UwU, y, width=0.005, align='center', label = 'Numerical result')  # width ~ spacing between your x values
    
    WTFErnesto = AnalyticalResult(r_real,2**n_count)
    plt.plot(WTFErnesto[0], WTFErnesto[1], color='orange', linewidth=1.5, linestyle='dotted', label='Analytical result')

    plt.xlabel(r"$\frac{d}{r}$", fontsize=16)
    plt.ylabel("Relative frequency")
    plt.legend(loc='upper right')
    
    plt.gca().xaxis.set_major_formatter(FuncFormatter(to_fraction))
    plt.tight_layout()
    
    # plt.hist(countsNumeric, bins = 1, range=(0, 2**n_count))

    # plot_histogram(countsNumeric,  title = f"N = {N}; n_count = {n_count}")
    plt.savefig(f"../Plots/FractionsPlotBinaryN{N}n_count{n_count}.jpg",dpi=300,bbox_inches='tight')
    matplot2tikz.save(f"../Plots/FractionsPlotBinaryN{N}n_count{n_count}..tex")
    plt.close()

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
            r_guess.append(frac.denominator)
    # Print the rows in a table
    # headers=["Register Output", "Phase", "Fraction", "Guess for r", "guess1","guess2"]
    headers = ["Register Output", "Fraction", "Guess for r", "guess1","guess2"]
    df      = pd.DataFrame(rows, columns=headers)

    df.to_csv(f'../Plots/FractionsPlotN{N}n_count{n_count}.csv', index=False)
    
    # Count occurrences of each unique value
    counting = Counter(r_guess)

    # Sort the values for nice x ordering
    x_OuO = sorted(counting.keys())
    y_OuO = [counting[k] for k in x_OuO]

    # Plot as a centered bar chart
    # plt.figure(figsize=(6,4))
    plt.bar(x_OuO, y_OuO, width=2, align='center')

    # Labels and style
    plt.xlabel(r"$r_{Guess}$", fontsize=16)
    plt.ylabel("Frequency")
    plt.xticks(x_OuO)  # Show only existing integer values (4, 8, 16)

    plt.savefig(f"../Plots/RGuessN{N}n_count{n_count}.jpg",dpi=300,bbox_inches='tight')
    matplot2tikz.save(f"../Plots/RGuessN{N}n_count{n_count}.tex")

    plt.close()


