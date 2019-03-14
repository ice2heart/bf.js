#!/usr/bin/env python3

import argparse
import pprint
from collections import OrderedDict
from copy import copy
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
        line = f'p({i2t(item.args[0])}, {i2t(item.args[1])})'
    elif item.type is '+':
        line = f'add(mem_point, {item.args[0]})'
    elif item.type is '-':
        line = f'add(mem_point, -{item.args[0]})'
    elif item.type is 'clear':
        line = f'{i2t(item.args[0])} = 0'
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

def i2t_j(item):
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
        line = f'index += {item.args[0]};'
    elif item.type is '<':
        line = f'index -= {item.args[0]};'
    elif item.type is PRINT:
        line = f'System.out.print(repeatChar((char) {i2t_j(item.args[1])}, {i2t_j(item.args[0])}));'
        # line = f'p({i2t_j(item.args[0])}, {i2t_j(item.args[1])})'
    elif item.type is '+':
        line = f'x[index] += {item.args[0]};'
    elif item.type is '-':
        line = f'x[index] -= {item.args[0]};'
    elif item.type is 'clear':
        line = f'{i2t_j(item.args[0])} = 0;'
    elif item.type is ',':
        line = 'x[index] = (byte) sc.next().charAt(0);'
    elif item.type is EQUALITY:
        line = f'{i2t_j(item.args[0])}=(byte)({i2t_j(item.args[1])});'
        # line += ';print(mem[:40]);input();'
    elif item.type is PLUS:
        line = f'{i2t_j(item.args[0])}+{i2t_j(item.args[1])}'
    elif item.type is SUB:
        line = f'{i2t_j(item.args[0])}-{i2t_j(item.args[1])}'
    elif item.type is RELATIVE_POINTER:
        if isinstance(item.args[0], int) and item.args[0] is 0:
            line = 'x[index]'
        else:
            line = f'x[index+{i2t_j(item.args[0])}]'
    elif item.type is MULTIPLICATION:
        line = f'{i2t_j(item.args[0])}*{i2t_j(item.args[1])}'
        if isinstance(item.args[0], float) or isinstance(item.args[1], float):
            line = f'(byte) ({line})'
    else:
        breakpoint()
        raise Exception(f'unknown symbol {item.type}')
    return line

def process_branch_java(branch, shift):
    text = ''
    if branch.type is CYCLE:
        line = 'while (x[index] != 0) {'
        text += ' ' * shift + line + '\n'
        shift += 4

    for i in branch.args:
        if i.type is CYCLE:
            text += process_branch_java(i, shift)
            continue
        line = i2t_j(i)
        text += ' ' * shift + line + '\n'
    if branch.type is CYCLE:
        text += ' ' * (shift-4)  + '}\n'
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

def generate_java(ast):
    text = '''
import java.util.Scanner;
import java.util.Arrays;


public class Main {
    private static final String repeatChar(char c, int length) {
        char[] data = new char[length];
        Arrays.fill(data, c);
        return new String(data);
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        byte[] x = new byte[32768];
        for (int xc = 0; xc < 32768; xc++)
            x[xc] = 0;
        int index = 0;
'''
    shift = 8
    text += process_branch_java(ast, shift)
    text +='''
    }
}'''
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


def update_relative_pointer(branch, shift):
    for i in branch.args:
        if isinstance(i, int) or isinstance(i, float):
            continue
        if i.type is RELATIVE_POINTER:
            i.args[0] += shift
        else:
            i = update_relative_pointer(i, shift)
    return branch

def loop_multiplication(branch):
    # branch.args = list(filter(lambda x: x is not None, branch.args))
    for i in branch.args:
        # if i.type is CYCLE:
        if i.type is CYCLE or i.type is EQUALITY:
            return branch
    move_sum = 0
    for i in branch.args:
        if i.type is '>':
            move_sum += i.args[0]
        if i.type is '<':
            move_sum -= i.args[0]
    if move_sum is not 0:
        # print(f'can be optimize {move_sum} {branch}')
        return branch
    relative_counter = 0
    operanads = list()
    for i in branch.args:
        if i.type is '>':
            relative_counter += i.args[0]
        elif i.type is '<':
            relative_counter -= i.args[0]
        else:
            operanads.append((relative_counter,i))

    step = [i for i in operanads if i[0] is 0]
    operanads = [i for i in operanads if i[0] is not 0]
    # print('step', step)
    if len(step) is not 1:
        return branch
    step = step[0][1]
    if step.type is not '-' and step.type is not '+':
        return branch
    # print('step', step, operanads)

    new_branch = Item(type='unwind', args=[])

    for o, operand in operanads:
        item = None
        if operand.type is '+' or operand.type is '-':
            r_type = PLUS
            if operand.type is '-':
                r_type = SUB
            base_value = Item(type=RELATIVE_POINTER, args=[o])
            if step.type is '+':
                base_value = Item(type=SUB, args=[
                    255,
                    Item(type=RELATIVE_POINTER, args=[o])
                ])
            item = Item(type=EQUALITY, args=[
                Item(type=RELATIVE_POINTER, args=[o]),
                Item(type=r_type, args=[
                    base_value,
                    Item(type=MULTIPLICATION, args=[
                        Item(type=RELATIVE_POINTER, args=[0]),
                        Item(type=MULTIPLICATION, args=[
                            operand.args[0],
                            (1 / step.args[0])
                        ])
                    ])
                ])
            ])
        elif operand.type is PRINT:
            base_value = Item(type=RELATIVE_POINTER, args=[0])
            if step.type is '+':
                base_value = Item(type=SUB, args=[
                    255,
                    Item(type=RELATIVE_POINTER, args=[0])
                ])
            item = Item(type=PRINT, args=[None, operand.args[1]])
            item.args[1].args[0] += o
            item.args[0] = Item(type=MULTIPLICATION, args=[
                operand.args[0],
                Item(type=MULTIPLICATION, args=[
                    base_value,
                    (1 / step.args[0])
                ])
            ])
        elif operand.type is EQUALITY:
            # print('operand', operand, o)
            operand = update_relative_pointer(operand, o)
            base_value = Item(type=RELATIVE_POINTER, args=[0])
            if step.type is '+':
                base_value = Item(type=SUB, args=[
                    255,
                    Item(type=RELATIVE_POINTER, args=[0])
                ])
            operand.args[1].args[1] = Item(type=MULTIPLICATION, args=[
                operand.args[1].args[1],
                Item(type=MULTIPLICATION, args=[
                    base_value,
                    (1 / step.args[0])
                ])
            ])
            # print('updated', operand, o)
            new_branch.args.append(operand)
        elif operand.type is 'clear':
            new_branch.args.append(update_relative_pointer(operand, o))
        else:
            raise Exception(f'panic! {operand.type}')
        new_branch.args.append(item)
    new_branch.args.append(Item(type='clear', args=[Item(type=RELATIVE_POINTER, args=[0])]))
    # print('multi', new_branch, branch)
    new_branch = symplify_multiplication(new_branch)
    return new_branch


def clear_branch(branch):
    branch.args = list(filter(lambda x: x is not None, branch.args))
    branch = unwind(branch)
    return branch


def symplify_multiplication(branch):
    for pos, item in enumerate(branch.args):
        if isinstance(item, int) or isinstance(item, float) or item is None:
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
        return Item(type='clear', args=[Item(type=RELATIVE_POINTER, args=[0])])
    if len(branch.args) == 0:
        return None
    branch = remove_repetitions(branch)
    branch = clear_branch(branch)
    for pos, i in enumerate(branch.args):
        if i is None:
            continue
        if i.type is CYCLE:
            i = optimize_branch(i)
            branch.args[pos] = i
            continue
    branch = clear_branch(branch)
    # branch = loop_multiplication(branch)
    # branch = clear_branch(branch)
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
    # pp.pprint(ast)
    java_code = generate_java(ast)
    with open('jt/Main.java', 'w') as file:
        file.write(java_code)
    text = generate_python(ast)
    with open('prog.py', 'w') as file:
        file.write(text)
    # print(text)


if __name__ == "__main__":
    main()
