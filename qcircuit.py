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

class WireStatus(Enum):
    ON = 0
    OFF = 1
    ELLIPSIS = 2
    CLASSICAL = 3

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

    def insertContent(self, wire, content, t=-1):
        if t == -1:
            t = len(self)
        column = self.getColumn(t)
        column[wire] = content

    def getLaTeXforCell(self, c, wire, wire_status):
        column = self.getColumn(c)
        for w in column:
            content = column[w]
            if isinstance(content, Ctrl) and w == wire:
                wire_status[wire] = WireStatus.ON
                return f"\\ctrl{{{content.target}}}"
            elif isinstance(content, Gate):
                if w == wire:
                    if content.size == 1:
                        wire_status[wire] = WireStatus.ON
                        return f"\\gate{{{content.name}}}"
                    else:
                        wire_status[wire] = WireStatus.ON
                        return f"\\multigate{{{content.size - 1}}}{{{content.name}}}"
                elif wire > w and wire < w + content.size:
                    wire_status[wire] = WireStatus.ON
                    return f"\\ghost{{{content.name}}}"
            elif isinstance(content, Input) and w == wire:
                wire_status[wire] = WireStatus.ON
                return f"\\lstick{{{content.value}}}"
            elif isinstance(content, Etc) and w == wire:
                wire_status[wire] = WireStatus.ELLIPSIS
                return f"\\cdots"
            # TODO elif measurement
        # Content not found - maybe just a wire?
        if wire_status[wire] == WireStatus.ON:
            return r"\qw"
        elif wire_status[wire] == WireStatus.ELLIPSIS:
            wire_status[wire] = WireStatus.ON
            return ""
        else:
            assert wire_status[wire] == WireStatus.OFF
            return ""

    def getLaTeX(self):
        wire_status = [WireStatus.OFF] * self.num_wires
        lines = [self.getLaTeXforCell(0, i, wire_status)
                    for i in range(self.num_wires)]
        for c in range(1, len(self)):
            for i in range(self.num_wires):
                lines[i] += f" & {self.getLaTeXforCell(c, i, wire_status)}"
        return functools.reduce(lambda a, b: f"{a} \\\\\n{b}", lines)

if __name__ == "__main__":
    ct = QCircuit(8)
    # start with control gates...
    t = 0
    ct.insertContent(0, Ctrl(1), t)
    ct.insertContent(1, Ctrl(1), t)
    ct.insertContent(2, Ctrl(1), t)
    ct.insertContent(3, Ctrl(-1), t)
    ct.insertContent(4, Input(r"\ket{\delta_1}"))
    t += 1

    print(ct.getLaTeX())
