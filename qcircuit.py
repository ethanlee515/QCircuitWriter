#!/usr/bin/env python3

import functools
from enum import Enum

class Measure:
    pass

# I want to use `Ellipsis` but that's a built-in class
class Etc:
    pass

class Ctrl:
    def __init__(self, target):
        self.target = target

class Gate:
    def __init__(self, name, size = 1):
        self.name = name
        self.size = size

class Input:
    def __init__(self, value):
        self.value = value

class Output:
    def __init__(self, value):
        self.value = value

class WireType(Enum):
    ON = 0
    OFF = 1
    CLASSICAL = 2

class WireStatus():
    def __init__(self):
        self.off()

    def qw(self):
        self.wire_type = WireType.ON
        self.ellipsis = False

    def cw(self):
        self.wire_type = WireType.CLASSICAL
        self.ellipsis = False

    def off(self):
        self.wire_type = WireType.OFF
        self.ellipsis = False

    def etc(self):
        self.ellipsis = True

class QCircuit:
    def __init__(self, num_wires):
        self.num_wires = num_wires
        self.columns = list()

    def __len__(self):
        return len(self.columns)

    def getColumn(self, t):
        if not (t < len(self.columns)):
            assert(t == len(self.columns))
            col = dict()
            self.columns.append(col)
        return self.columns[t]

    def insert(self, wire, content, t=-1):
        if t == -1:
            t = len(self)
        column = self.getColumn(t)
        column[wire] = content

    def getLaTeXforCell(self, c, wire, wire_status):
        column = self.getColumn(c)
        for w in column:
            content = column[w]
            if isinstance(content, Ctrl) and w == wire:
                wire_status[wire].qw()
                return f"\\ctrl{{{content.target}}}"
            elif isinstance(content, Gate):
                if w == wire:
                    if content.size == 1:
                        wire_status[wire].qw()
                        return f"\\gate{{{content.name}}}"
                    else:
                        wire_status[wire].qw()
                        return f"\\multigate{{{content.size - 1}}}{{{content.name}}}"
                elif wire > w and wire < w + content.size:
                    wire_status[wire].qw()
                    return f"\\ghost{{{content.name}}}"
            elif isinstance(content, Input) and w == wire:
                wire_status[wire].qw()
                return f"\\lstick{{{content.value}}}"
            elif isinstance(content, Output) and w == wire:
                if wire_status[wire].wire_type == WireType.ON:
                    x = r"\qw"
                else:
                    x = r"\cw"
                wire_status[wire].off()
                return f"\\rstick{{{content.value}}}{x}"
            elif isinstance(content, Measure) and w == wire:
                wire_status[wire].cw()
                return f"\\meter"
            elif isinstance(content, Etc):
                wire_status[wire].etc()
                if w == wire:
                    return f"\\cdots"
                else:
                    return ""
        # Content not found - maybe just a wire?
        wiretype = wire_status[wire].wire_type;
        if wiretype == WireType.ON:
            if wire_status[wire].ellipsis:
                wire_status[wire].ellipsis = False
                return ""
            else:
                return r"\qw"
        elif wiretype == WireType.CLASSICAL:
            if wire_status[wire].ellipsis:
                wire_status[wire].ellipsis = False
                return ""
            else:
                return r"\cw"
        else:
            assert wiretype == WireType.OFF
            return ""

    def getLaTeX(self):
        wire_status = list()
        for i in range(self.num_wires):
            wire_status.append(WireStatus())
        lines = [self.getLaTeXforCell(0, i, wire_status)
                    for i in range(self.num_wires)]
        for c in range(1, len(self)):
            for i in range(self.num_wires):
                lines[i] += f" & {self.getLaTeXforCell(c, i, wire_status)}"
        return functools.reduce(lambda a, b: f"{a} \\\\\n{b}", lines)

if __name__ == "__main__":
    ct = QCircuit(8)
    # Inputs
    t = 0
    ct.insert(4, Input(r"\ket{0}"), t)
    # Setting up the graph edges
    t += 1
    ct.insert(0, Ctrl(1), t)
    ct.insert(1, Ctrl(1), t)
    ct.insert(2, Ctrl(1), t)
    ct.insert(3, Ctrl(-1), t)
    ct.insert(5, Input(r"\ket{\delta_1}"), t)
    # Honest behavior 1
    t += 1
    ct.insert(0, Gate(r"T^{\delta_1}"), t)
    ct.insert(5, Ctrl(-5), t)
    t += 1
    ct.insert(0, Gate("H"), t)
    # Attack 1
    t += 1
    ct.insert(0, Gate("U_1", 6), t)
    # Measure 1
    t += 1
    ct.insert(0, Measure(), t)
    # output and new delta
    t += 1
    ct.insert(0, Output("b_1"), t)
    ct.insert(6, Input(r"\ket{\delta_2}"), t)
    # Honest behavior 2
    t += 1
    ct.insert(1, Gate(r"T^{\delta_2}"), t)
    ct.insert(6, Ctrl(-5), t)
    t += 1
    ct.insert(1, Gate("H"), t)
    # Attack 2
    t += 1
    ct.insert(1, Gate("U_2", 6), t)
    # Measure 2 and output 2
    t += 1
    ct.insert(1, Measure(), t)
    t += 1
    ct.insert(1, Output("b_2"), t)
    # Ellipsis
    t += 1
    ct.insert(3, Etc(), t)
    # delta t
    t += 1
    ct.insert(7, Input(r"\ket{\delta_t}"), t)
    # Honest behavior T
    # TODO LaTeX macro?
    t += 1
    ct.insert(2, Gate(r"T^{\delta_t}"), t)
    ct.insert(7, Ctrl(-5), t)
    

    print(ct.getLaTeX())
