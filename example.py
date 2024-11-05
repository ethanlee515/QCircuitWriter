#!/usr/bin/env python3

from qcircuit import *

ct = QCircuit(10)
# Inputs
t = 0
ct.insert(5, Input(r"\ket{0}"), t)
# Empty inputs to turn on wires for now
for i in range(5):
    ct.insert(i, Input(""), t)
# Mark where there are multiple wires
t += 1
ct.insert(2, MultipleWires(), t)
ct.insert(4, MultipleWires(), t)
# Setting up the graph edges
t += 1
ct.insert(0, Ctrl(1), t)
ct.insert(1, Ctrl(1), t)
ct.insert(2, Ctrl(1), t)
ct.insert(3, Ctrl(1), t)
ct.insert(4, Ctrl(-1), t)
ct.insert(6, Input(r"\ket{\delta_1}"), t)
# Honest behavior 1
t += 1
t1 = t
ct.insert(0, Gate(r"T^{\delta_1}"), t)
ct.insert(6, Ctrl(-6), t)
t += 1
ct.insert(0, Gate("H"), t)
# Attack 1
t += 1
ct.insert(0, Gate("U_1", 7), t)
# Measure 1
t += 1
ct.insert(0, Measure(), t)
# output and new delta
t += 1
ct.insert(0, Output("b_1"), t)
ct.insert(7, Input(r"\ket{\delta_2}"), t)
# Honest behavior 2
t += 1
t2 = t
ct.insert(1, Gate(r"T^{\delta_2}"), t)
ct.insert(7, Ctrl(-6), t)
t += 1
ct.insert(1, Gate("H"), t)
# Attack 2
t += 1
ct.insert(1, Gate("U_2", 7), t)
# Measure 2 and output 2
t += 1
ct.insert(1, Measure(), t)
t += 1
ct.insert(1, Output("b_2"), t)
# Ellipsis
t += 1
t_ellipsis = t
ct.insert(2, WireOff(), t)
ct.insert(4, Etc(), t)
# delta t
t += 1
ct.insert(8, Input(r""), t)
t += 1
ct.insert(8, MultipleWires(), t)
ct.insert(9, Input(r"\ket{\delta_t}"), t)
# Honest behavior T
# TODO LaTeX macro?
t += 1
tt = t
ct.insert(3, Gate(r"T^{\delta_t}"), t)
ct.insert(9, Ctrl(-6), t)
t += 1
ct.insert(3, Gate("H"), t)
# Attack t
t += 1
ct.insert(3, Gate("U_t", 7), t)
# Measure t
t += 1
ct.insert(3, Measure(), t)
t += 1
ct.insert(3, Output("b_t"), t)
# final output
t += 1
ct.insert(4, Output(r"\sigma_{out}"), t)

print("first figure:")
print(ct.getLaTeX())
print()

# Second figure now
## Remove measurements
ct.delete(0, t1 + 3)
ct.delete(0, t1 + 4)
ct.delete(1, t2 + 3)
ct.delete(1, t2 + 4)
## Remove wireoff
ct.delete(2, t_ellipsis)
'''
ct.delete(3, tt + 3)
ct.delete(3, tt + 4)
ct.delete(2, tt - 2)
'''
## Move deltas
ct.delete(6, t1 - 1)
ct.insert(6, Input(r"\ket{\delta_1}"), 0)
ct.delete(7, t2 - 1)
ct.insert(7, Input(r"\ket{0}"), 0)
ct.delete(8, t_ellipsis + 1)
ct.delete(8, t_ellipsis + 2)
ct.insert(8, Input(r"\ket{0}"), 0)
ct.insert(8, MultipleWires(), 1)
ct.delete(9, tt - 1)
ct.insert(9, Input(r"\ket{0}"), 0)
## Add wire for delta 3
ct.addWire(8)
ct.insert(8, Input(r"\ket{0}"), 0)
## Add secret wire
ct.addWire(0)
ct.insert(0, Input(r"\ket{\nu}"), 0)
## Compute first delta
ct.addCol(t1 + 3)
ct.insert(0, Ctrl(1), t1 + 3)
ct.insert(1, Ctrl(7), t1 + 3)
ct.insert(8, Gate(r"X^{\delta_2}"), t1 + 3)
## Compute second delta
t2 += 1
ct.addCol(t2 + 3)
ct.insert(0, Ctrl(1), t2 + 3)
ct.insert(1, Ctrl(1), t2 + 3)
ct.insert(2, Ctrl(7), t2 + 3)
ct.insert(9, Gate(r"X^{\delta_3}"), t2 + 3)
tt += 2
## Compute last delta
ct.insert(0, Ctrl(1), t_ellipsis + 4)
ct.insert(1, Ctrl(1), t_ellipsis + 4)
ct.insert(2, Ctrl(1), t_ellipsis + 4)
ct.insert(3, Ctrl(8), t_ellipsis + 4)
ct.insert(11, Gate(r"X^{\delta_t}"), t_ellipsis + 4)
## Measure all b_i
ct.insert(0, Measure(), tt + 3)
ct.insert(0, Output(r"\nu"), tt + 4)
ct.insert(1, Measure(), tt + 3)
ct.insert(1, Output(r"b_1"), tt + 4)
ct.insert(2, Measure(), tt + 3)
ct.insert(2, Output(r"b_2"), tt + 4)
ct.insert(3, Measure(), tt + 3)
ct.insert(3, Output(r"b_3,\ldots,b_{t-1}"), tt + 4)
ct.insert(4, Measure(), tt + 3)
ct.insert(4, Output(r"b_t"), tt + 4)
print("second figure:")
print(ct.getLaTeX())
print()

# Last figure

ct.delete(1, t1 + 2)
ct.insert(1, Gate("Q_1"), t1 + 2)

ct.delete(2, t2 + 2)
ct.insert(2, Gate("Q_2"), t2 + 2)

ct.delete(4, tt + 2)
ct.insert(4, Gate("Q_t"), tt + 2)
ct.insert(5, Gate(r"V^Q", 7), tt + 2)

print("Third figure:")
print(ct.getLaTeX())
# TODO U_1 and U_2 have wrong size...
