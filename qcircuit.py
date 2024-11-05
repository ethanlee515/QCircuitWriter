#!/usr/bin/env python3

import functools
from enum import Enum

class Measure:
    pass

# I want to use `Ellipsis` but that's a built-in class
class Etc:
    pass

class MultipleWires:
    pass

class WireOff:
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

    """
    Clears a gate (or anything else).
    If multigate, clears the ghosts too.
    """
    def delete(self, wire, t):
        del self.columns[t][wire]

    def addWire(self, h):
        assert(0 <= h)
        assert(h <= self.num_wires)
        self.num_wires += 1
        columns = list()
        for col in self.columns:
            new_col = dict()
            for w in col:
                # enlarge CTRL if it crosses the new wire
                content = col[w]
                if isinstance(content, Ctrl):
                    if w < h and w + content.target >= h:
                        content.target += 1
                    elif w >= h and w + content.target < h:
                        content.target -= 1
                # enlarge multigate if it crosses the new wire
                if isinstance(content, Gate):
                    if w < h and w + content.size - 1 >= h:
                        content.size += 1
                if w < h:
                    new_col[w] = content
                else:
                    new_col[w + 1] = content
            columns.append(new_col)
        self.columns = columns

    def addCol(self, t):
        self.columns.insert(t, dict())

    def delCol(self, t):
        del self.columns[t]

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
            elif isinstance(content, MultipleWires) and w == wire:
                wire_status[wire].qw()
                return r"{/} \qw"
            elif isinstance(content, WireOff) and w == wire:
                wire_status[wire].off()
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
