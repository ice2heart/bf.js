#!/usr/bin/env python3

import argparse
import pprint
from collections import OrderedDict
pp = pprint.PrettyPrinter(indent=2)

SYMBLS = ['+', '-', '>', '<', '[', ']', '.', ',']
REPITABLE = ['+', '-', '>', '<', '.']
CYCLE = 'cycle'
MULTIPLICATION = 'multi'
EQUALITY = 'eq'
PLUS = 'plus'
SUB = 'substraction'
RELATIVE_POINTER = 'rpoint'
UNWIND = 'unwind'
PRINT = '.'


class Item:
    type = ''
    parent = None
    args = []

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.type}: {self.args}'


def i2t(item):
    # item to text
    line = ''
    if isinstance(item, int):
        if item >= 0:
            line = str(item)
        else:
            line = f'({str(item)})'
    elif isinstance(item, float):
        if item >= 0:
            line = str(item)
        else:
            line = f'({str(item)})'
    elif item.type is '>':
        line = f'mem_point = mem_point + {item.args[0]}'
    elif item.type is '<':
        line = f'mem_point = mem_point - {item.args[0]}'
    elif item.type is PRINT:
        line = f'p({item.args[0]}, {i2t(item.args[1])})'
    elif item.type is '+':
        line = f'add(mem_point, {item.args[0]})'
    elif item.type is '-':
        line = f'add(mem_point, -{item.args[0]})'
    elif item.type is 'clear':
        line = 'mem[mem_point] = 0'
    elif item.type is ',':
        line = 'mem[mem_point] = read()'
    elif item.type is EQUALITY:
        line = f'{i2t(item.args[0])}={i2t(item.args[1])}'
        # line += ';print(mem[:40]);input();'
    elif item.type is PLUS:
        line = f'(int({i2t(item.args[0])}+{i2t(item.args[1])})& 0xFF )'
    elif item.type is SUB:
        line = f'(int({i2t(item.args[0])}-{i2t(item.args[1])})& 0xFF )'
    elif item.type is RELATIVE_POINTER:
        if isinstance(item.args[0], int) and item.args[0] is 0:
            line = f'mem[mem_point]'
        else:
            line = f'mem[mem_point+{i2t(item.args[0])}]'
    elif item.type is MULTIPLICATION:
        line = f'{i2t(item.args[0])}*{i2t(item.args[1])}'
    else:
        breakpoint()
        raise Exception(f'unknown symbol {item.type}')
    return line


def process_branch(branch, shift):
    text = ''
    if branch.type is CYCLE:
        line = 'while mem[mem_point] != 0:'
        text += ' ' * shift + line + '\n'
        shift += 2

    for i in branch.args:
        if i.type is CYCLE:
            text += process_branch(i, shift)
            continue
        line = i2t(i)
        text += ' ' * shift + line + '\n'
    return text


def generate_python(ast):
    text = '''mem = [0] * 30000
mem_point = 0
def add(point, val):
    mem[point] = (mem[point] + val) & 0xFF
def p(times, char):
    print(chr(char) * times, end=\'\')
def read():
    i=0
    try:
        i=ord(input(\'>\'))
    except TypeError:
        pass
    return i
'''
    shift = 0
    text += process_branch(ast, shift)
    return text


def remove_repetitions(branch):
    for pos, i in enumerate(branch.args):
        count = 1
        if i is None:
            continue
        if i.type not in REPITABLE:
            continue
        try:
            while True:
                if branch.args[pos+count].type == i.type:
                    count += 1
                else:
                    break
        except IndexError:
            pass
        branch.args[pos].args[0] = count
        if count > 1:
            while count != 1:
                branch.args[pos+count-1] = None
                count -= 1
    return branch


def unwind(branch):
    while True:
        index = -1
        for pos, i in enumerate(branch.args):
            if i.type is UNWIND:
                index = pos
                break
        if index is -1:
            break
        item = branch.args.pop(index)
        branch.args[index:index] = item.args
    return branch


def loop_multiplication(branch):
    branch.args = list(filter(lambda x: x is not None, branch.args))
    for i in branch.args:
        if i.type is CYCLE or i.type is '.':
            return branch
    move_sum = 0
    for i in branch.args:
        if i.type is '>':
            move_sum += i.args[0]
        if i.type is '<':
            move_sum -= i.args[0]
    if move_sum is not 0:
        return branch
    relative_counter = 0
    operanads = OrderedDict()
    for i in branch.args:
        if i.type is '>':
            relative_counter += i.args[0]
        elif i.type is '<':
            relative_counter -= i.args[0]
        else:
            if relative_counter not in operanads:
                operanads[relative_counter] = i
            else:
                if operanads[relative_counter].type == i.type:
                    # print('same', operanads[relative_counter], i)
                    operanads[relative_counter].args[0] += i.args[0]
                else:
                    print(operanads[relative_counter])
                    raise Exception('type mismatch')
    new_branch = Item(type='unwind', args=[])
    direction = -1
    step = operanads.pop(0)
    if step.type is '+':
        direction = 1

    for o in operanads.keys():
        r_type = PLUS
        if operanads[o].type is '-':
            r_type = SUB
        if direction is -1:
            item = Item(type=EQUALITY, args=[
                Item(type=RELATIVE_POINTER, args=[o]),
                Item(type=r_type, args=[
                    Item(type=RELATIVE_POINTER, args=[o]),
                    Item(type=MULTIPLICATION, args=[
                        Item(type=RELATIVE_POINTER, args=[0]),
                        Item(type=MULTIPLICATION, args=[
                            operanads[o].args[0],
                            (1 / step.args[0])
                        ])
                    ])
                ])
            ])
            new_branch.args.append(item)
        else:
            # print(f'mem[point+({o})] += (255 - mem[point]) * {operanads[o].args[0]} * (1/step)')
            item = Item(type=EQUALITY, args=[
                Item(type=RELATIVE_POINTER, args=[o]),
                Item(type=r_type, args=[
                    Item(type=SUB, args=[
                        255,
                        Item(type=RELATIVE_POINTER, args=[o])
                    ]),
                    Item(type=MULTIPLICATION, args=[
                        Item(type=RELATIVE_POINTER, args=[0]),
                        Item(type=MULTIPLICATION, args=[
                            operanads[o].args[0],
                            (1 / step.args[0])
                        ])
                    ])
                ])
            ])
            # raise Exception('not emplimented')
            new_branch.args.append(item)
        # print(operanads[o].type, o, operanads[o].args[0])
    new_branch.args.append(Item(type='clear'))
    # print('multi', new_branch, branch)
    new_branch = symplify_multiplication(new_branch)
    return new_branch


def clear_branch(branch):
    branch.args = list(filter(lambda x: x is not None, branch.args))
    branch = unwind(branch)
    return branch


def symplify_multiplication(branch):
    for pos, item in enumerate(branch.args):
        if isinstance(item, int) or isinstance(item, float):
            pass
        elif item.type is MULTIPLICATION:
            item = symplify_multiplication(item)
            if (isinstance(item.args[1], int) or isinstance(item.args[1], float)) and int(item.args[1]) is 1:
                branch.args[pos] = item.args[0]
            elif (isinstance(item.args[0], int) or isinstance(item.args[0], float)) and int(item.args[0]) is 1:
                branch.args[pos] = item.args[1]
        else:
            item = symplify_multiplication(item)
    return branch


def optimize_branch(branch):
    if len(branch.args) == 1 and (branch.args[0].type == '-' or branch.args[0].type == '+'):
        return Item(type='clear')
    if len(branch.args) == 0:
        return None
    branch = remove_repetitions(branch)
    branch = clear_branch(branch)
    branch = loop_multiplication(branch)
    branch = clear_branch(branch)
    for pos, i in enumerate(branch.args):
        if i is None:
            continue
        if i.type is CYCLE:
            i = optimize_branch(i)
            branch.args[pos] = i
            continue
    branch = clear_branch(branch)
    return branch


def optimize_ast(ast):
    if ast is None:
        raise Exception('no program')
    ast = optimize_branch(ast)
    return ast


def main():
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('filename', type=str, help='File to parse')
    args = parser.parse_args()
    program = []
    with open(args.filename, 'r') as file:
        for i in file.read():
            if i in SYMBLS:
                program.append(i)
    ast = Item(args=[], type='Prog')
    parent = ast
    for code_item in program:
        if code_item is '[':
            item = Item(parent=parent, args=[], type=CYCLE)
            parent.args.append(item)
            parent = item
            continue
        if code_item is ']':
            parent = parent.parent
            continue
        item = Item(parent=parent, args=[1], type=code_item)
        if item.type is PRINT:
            item.args.append(Item(type=RELATIVE_POINTER, args=[0]))
        parent.args.append(item)
    # pp.pprint(ast)
    ast = optimize_ast(ast)
    pp.pprint(ast)
    text = generate_python(ast)
    with open('prog.py', 'w') as file:
        file.write(text)
    # print(text)


if __name__ == "__main__":
    main()
