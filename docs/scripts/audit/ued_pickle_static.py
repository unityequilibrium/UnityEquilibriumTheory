"""Inert pickle syntax interpreter. Never imports or invokes serialized globals.

Not a general unpickler: numeric buffers become summaries; all other objects
remain inert nodes. Unsupported syntax, object buffers and oversized reads fail.
"""

from dataclasses import dataclass, field
import hashlib
import pickletools

import numpy as np


@dataclass
class Node:
    kind: str
    args: object
    state: object = None


@dataclass
class Buffer:
    data: object
    size: int = field(init=False)
    sha256: str = field(init=False)
    cached: dict = field(default_factory=dict)

    def __post_init__(self):
        self.size = len(self.data)
        self.sha256 = hashlib.sha256(self.data).hexdigest()


class BoundedReader:
    def __init__(self, stream, maximum=1024**3):
        self.stream, self.remaining = stream, maximum

    def read(self, size=-1):
        if size < 0 or size > 16*1024**2 or size > self.remaining:
            raise ValueError('pickle read budget exceeded')
        data = self.stream.read(size)
        self.remaining -= len(data)
        return data

    def readline(self):
        result = self.stream.readline(65537)
        if len(result) > 65536 or len(result) > self.remaining:
            raise ValueError('pickle line budget exceeded')
        self.remaining -= len(result)
        return result

    def tell(self):
        return self.stream.tell()


def numeric_summary(args, numeric_sink=None):
    buffer, dtype, shape, order = args
    if not isinstance(buffer, Buffer) or not isinstance(dtype, Node):
        raise ValueError('unsupported numeric buffer')
    target, params = dtype.args
    if target != Node('GLOBAL', ('numpy', 'dtype')):
        raise ValueError('dtype must be an inert numpy dtype declaration')
    code = params[0]
    allowed = {'f4', 'f8', 'i1', 'i2', 'i4', 'i8', 'u1', 'u2', 'u4', 'u8', 'b1'}
    if code not in allowed or not isinstance(shape, tuple) or order not in ('C', 'F'):
        raise ValueError('unsupported dtype, shape or order')
    if not shape or any(type(v) is not int or v < 0 for v in shape):
        raise ValueError('invalid numeric shape')
    endian = dtype.state[1] if dtype.state is not None else '='
    if endian not in ('<', '>', '=', '|'):
        raise ValueError('invalid byte order')
    dt = np.dtype(endian+code)
    count = 1
    for v in shape:
        count *= v
    if count*dt.itemsize != buffer.size:
        raise ValueError('numeric shape/byte count mismatch')
    key = (dt.str, shape, order)
    if key in buffer.cached:
        return buffer.cached[key]
    if buffer.data is None:
        raise ValueError('buffer reinterpreted after release')
    array = np.frombuffer(buffer.data, dtype=dt).reshape(shape, order=order)
    finite = np.isfinite(array)
    record = dict(shape=list(shape), dtype=dt.str, order=order, sha256=buffer.sha256,
                  bytes=buffer.size, finite_count=int(finite.sum()), count=count)
    if count and finite.all():
        record.update(minimum=float(array.min()), maximum=float(array.max()), mean=float(array.mean()))
    if count <= 8192:
        record['values'] = array.tolist()
    if numeric_sink is not None:
        view = array.view()
        view.flags.writeable = False
        numeric_sink(view, dict(record))
    buffer.cached[key] = Node('NUMERIC', record)
    buffer.data = None
    return buffer.cached[key]


def read_inert(stream, *, numeric_sink=None):
    stack, memo, marker = [], {}, object()
    globals_seen = set()

    def marked():
        values = []
        while stack and stack[-1] is not marker:
            values.append(stack.pop())
        if not stack:
            raise ValueError('missing mark')
        stack.pop()
        return values[::-1]

    for number, (op, arg, _) in enumerate(pickletools.genops(BoundedReader(stream))):
        if number > 1000000:
            raise ValueError('opcode budget exceeded')
        name = op.name
        if name in ('PROTO', 'FRAME'):
            continue
        if name == 'MARK': stack.append(marker)
        elif name == 'NONE': stack.append(None)
        elif name in ('NEWTRUE', 'NEWFALSE'): stack.append(name == 'NEWTRUE')
        elif name in ('BININT', 'BININT1', 'BININT2', 'INT', 'LONG', 'LONG1', 'LONG4', 'BINFLOAT', 'FLOAT', 'UNICODE', 'BINUNICODE', 'SHORT_BINUNICODE', 'BINUNICODE8'):
            stack.append(arg)
        elif name in ('SHORT_BINBYTES', 'BINBYTES', 'BINBYTES8', 'BYTEARRAY8'):
            stack.append(Buffer(arg))
        elif name == 'EMPTY_TUPLE': stack.append(())
        elif name == 'EMPTY_LIST': stack.append([])
        elif name == 'EMPTY_DICT': stack.append({})
        elif name == 'TUPLE': stack.append(tuple(marked()))
        elif name in ('TUPLE1', 'TUPLE2', 'TUPLE3'):
            count = int(name[-1]); values = tuple(stack[-count:]); del stack[-count:]; stack.append(values)
        elif name == 'APPEND': value = stack.pop(); stack[-1].append(value)
        elif name == 'APPENDS': values = marked(); stack[-1].extend(values)
        elif name == 'SETITEM': value, key = stack.pop(), stack.pop(); stack[-1][key] = value
        elif name == 'SETITEMS':
            values = marked()
            if len(values) % 2: raise ValueError('odd dictionary items')
            stack[-1].update(zip(values[::2], values[1::2]))
        elif name in ('BINPUT', 'LONG_BINPUT', 'PUT'): memo[arg] = stack[-1]
        elif name == 'MEMOIZE': memo[len(memo)] = stack[-1]
        elif name in ('BINGET', 'LONG_BINGET', 'GET'): stack.append(memo[arg])
        elif name in ('GLOBAL', 'STACK_GLOBAL'):
            if name == 'GLOBAL': module, symbol = arg.split(' ', 1)
            else: symbol, module = stack.pop(), stack.pop()
            if not isinstance(module, str) or not isinstance(symbol, str): raise ValueError('invalid global')
            globals_seen.add((module, symbol)); stack.append(Node('GLOBAL', (module, symbol)))
        elif name in ('REDUCE', 'NEWOBJ'):
            args, target = stack.pop(), stack.pop()
            if target in (Node('GLOBAL', ('numpy.core.numeric', '_frombuffer')), Node('GLOBAL', ('numpy._core.numeric', '_frombuffer'))):
                stack.append(numeric_summary(args, numeric_sink=numeric_sink))
            else: stack.append(Node(name, (target, args)))
        elif name == 'BUILD':
            state = stack.pop()
            if not isinstance(stack[-1], Node): raise ValueError('unsupported BUILD target')
            stack[-1].state = state
        elif name == 'STOP':
            if len(stack) != 1: raise ValueError('invalid final stack')
            return stack[0], sorted(globals_seen)
        else:
            raise ValueError('unsupported opcode: '+name)
    raise ValueError('no STOP')
