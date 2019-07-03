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


class CodeGenerator:
    def i2t(self, item):
        line = ''
        return line

    def process_branch(self, branch, shift):
        return ''

    def generate(self, ast):
        return ''


class JavaGenerator(CodeGenerator):
    def i2t(self, item):
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
            line = f'System.out.print(repeatChar((char) {self.i2t(item.args[1])}, {self.i2t(item.args[0])}));'
            # line = f'p({self.i2t(item.args[0])}, {self.i2t(item.args[1])})'
        elif item.type is '+':
            line = f'x[index] += {item.args[0]};'
        elif item.type is '-':
            line = f'x[index] -= {item.args[0]};'
        elif item.type is 'clear':
            line = f'{self.i2t(item.args[0])} = 0;'
        elif item.type is ',':
            line = 'x[index] = (byte) sc.next().charAt(0);'
        elif item.type is EQUALITY:
            line = f'{self.i2t(item.args[0])}=(byte)({self.i2t(item.args[1])});'
            # line += ';print(mem[:40]);input();'
        elif item.type is PLUS:
            line = f'{self.i2t(item.args[0])}+{self.i2t(item.args[1])}'
        elif item.type is SUB:
            line = f'{self.i2t(item.args[0])}-{self.i2t(item.args[1])}'
        elif item.type is RELATIVE_POINTER:
            if isinstance(item.args[0], int) and item.args[0] is 0:
                line = 'x[index]'
            else:
                line = f'x[index+{self.i2t(item.args[0])}]'
        elif item.type is MULTIPLICATION:
            line = f'{self.i2t(item.args[0])}*{self.i2t(item.args[1])}'
            if isinstance(item.args[0], float) or isinstance(item.args[1], float):
                line = f'(byte) ({line})'
        else:
            breakpoint()
            raise Exception(f'unknown symbol {item.type}')
        return line

    def process_branch(self, branch, shift):
        text = ''
        if branch.type is CYCLE:
            line = 'while (x[index] != 0) {'
            text += ' ' * shift + line + '\n'
            shift += 4

        for i in branch.args:
            if i.type is CYCLE:
                text += self.process_branch(i, shift)
                continue
            line = self.i2t(i)
            text += ' ' * shift + line + '\n'
        if branch.type is CYCLE:
            text += ' ' * (shift-4) + '}\n'
        return text

    def generate(self, ast):
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
        text += self.process_branch(ast, shift)
        text += '''
    }
}'''
        return text


class CGenerator(CodeGenerator):
    def i2t(self, item):
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
            line = f'repeat({self.i2t(item.args[1])}, {self.i2t(item.args[0])});'
        elif item.type is '+':
            line = f'x[index] += {item.args[0]};'
        elif item.type is '-':
            line = f'x[index] -= {item.args[0]};'
        elif item.type is 'clear':
            line = f'{self.i2t(item.args[0])} = 0;'
        elif item.type is ',':
            line = 'x[index] = (char) sc.next().charAt(0);'
        elif item.type is EQUALITY:
            line = f'{self.i2t(item.args[0])}=(char)({self.i2t(item.args[1])});'
            # line += ';print(mem[:40]);input();'
        elif item.type is PLUS:
            line = f'{self.i2t(item.args[0])}+{self.i2t(item.args[1])}'
        elif item.type is SUB:
            line = f'{self.i2t(item.args[0])}-{self.i2t(item.args[1])}'
        elif item.type is RELATIVE_POINTER:
            if isinstance(item.args[0], int) and item.args[0] is 0:
                line = 'x[index]'
            else:
                line = f'x[index+{self.i2t(item.args[0])}]'
        elif item.type is MULTIPLICATION:
            line = f'{self.i2t(item.args[0])}*{self.i2t(item.args[1])}'
            if isinstance(item.args[0], float) or isinstance(item.args[1], float):
                line = f'(char) ({line})'
        else:
            breakpoint()
            raise Exception(f'unknown symbol {item.type}')
        return line

    def process_branch(self, branch, shift):
        text = ''
        if branch.type is CYCLE:
            line = 'while (x[index] != 0) {'
            text += ' ' * shift + line + '\n'
            shift += 4

        for i in branch.args:
            if i.type is CYCLE:
                text += self.process_branch(i, shift)
                continue
            line = self.i2t(i)
            text += ' ' * shift + line + '\n'
        if branch.type is CYCLE:
            text += ' ' * (shift-4) + '}\n'
        return text

    def generate(self, ast):
        text = '''
#include <stdio.h>

void repeat(char c, int num) {
	for (int i=0; i< num; ++i){
		putchar(c);
	}
}
        
int main() {
    char x[32768] = { 0 };
    int index = 0;

'''
        shift = 4
        text += self.process_branch(ast, shift)
        text += '''
    return 0;
}'''
        return text


class VariableCounter:
    variables = {}

    def __getitem__(self, key):
        if key not in self.variables:
            self.variables[key] = 0
        return f'{key}.{self.variables[key]}'

    def __contains__(self, key):
        return kei in self.variables

    def set(self, key):
        if key not in self.variables:
            self.variables[key] = 0
        else:
            self.variables[key] += 1
        return f'{key}.{self.variables[key]}'


v = VariableCounter()


class LLVMGenerator(CodeGenerator):

    def i2t(self, item):
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
            line = f'''
  %{v.set('pointer_value')} = load i64, i64* %{v['pointer_ptr']}, align 8
  %{v.set('pointer_value_result')} = add i64 %{v['pointer_value']}, {item.args[0]}
  store i64 %{v['pointer_value_result']}, i64* %{v['pointer_ptr']}, align 8
'''
        elif item.type is '<':
            line = f'''
  %{v.set('pointer_value')} = load i64, i64* %{v['pointer_ptr']}, align 8
  %{v.set('pointer_value_result')} = sub i64 %{v['pointer_value']}, {item.args[0]}
  store i64 %{v['pointer_value_result']}, i64* %{v['pointer_ptr']}, align 8
'''
        elif item.type is PRINT:
            line = f'repeat({self.i2t(item.args[1])}, {self.i2t(item.args[0])});'
            line = f'''
  %{v.set('pointer_value')} = load i64, i64* %{v['pointer_ptr']}, align 8
  %{v.set('data_val_ptr')} = getelementptr inbounds [4000 x i8], [4000 x i8]* %{v['data_ptr']}, i64 0, i64 %{v['pointer_value']}
  %{v.set('data_val')} = load i8, i8* %{v['data_val_ptr']}, align 1
  %{v.set('data_val_ext')} = zext i8 %{v['data_val']} to i32
  %{v.set('call_putchar')} = tail call i32 @putchar(i32 %{v['data_val_ext']})
'''
        elif item.type is '+':
            line = f'''
  %{v.set('pointer_value')} = load i64, i64* %{v['pointer_ptr']}, align 8
  %{v.set('data_val_ptr')} = getelementptr inbounds [4000 x i8], [4000 x i8]* %{v['data_ptr']}, i64 0, i64 %{v['pointer_value']}
  %{v.set('data_val')} = load i8, i8* %{v['data_val_ptr']}, align 1
  %{v.set('data_val_result')} = add i8 %{v['data_val']}, {item.args[0]}
  store i8 %{v['data_val_result']}, i8* %{v['data_val_ptr']}, align 1
'''
        elif item.type is '-':
                        line = f'''
  %{v.set('pointer_value')} = load i64, i64* %{v['pointer_ptr']}, align 8
  %{v.set('data_val_ptr')} = getelementptr inbounds [4000 x i8], [4000 x i8]* %{v['data_ptr']}, i64 0, i64 %{v['pointer_value']}
  %{v.set('data_val')} = load i8, i8* %{v['data_val_ptr']}, align 1
  %{v.set('data_val_result')} = sub i8 %{v['data_val']}, {item.args[0]}
  store i8 %{v['data_val_result']}, i8* %{v['data_val_ptr']}, align 1
'''
        elif item.type is 'clear':
            line = f'{self.i2t(item.args[0])} = 0;'
            line = f'''

  %{v.set('pointer_value')} = load i64, i64* %{v['pointer_ptr']}, align 8
  %{v.set('data_val_ptr')} = getelementptr inbounds [4000 x i8], [4000 x i8]* %{v['data_ptr']}, i64 0, i64 %{v['pointer_value']}
  store i8 0, i8* %{v['data_val_ptr']}, align 1
'''
        elif item.type is ',':
            line = 'x[index] = (char) sc.next().charAt(0);'
        elif item.type is EQUALITY:
            line = f'{self.i2t(item.args[0])}=(char)({self.i2t(item.args[1])});'
            # line += ';print(mem[:40]);input();'
        elif item.type is PLUS:
            line = f'{self.i2t(item.args[0])}+{self.i2t(item.args[1])}'
        elif item.type is SUB:
            line = f'{self.i2t(item.args[0])}-{self.i2t(item.args[1])}'
        elif item.type is RELATIVE_POINTER:
            if isinstance(item.args[0], int) and item.args[0] is 0:
                line = 'x[index]'
            else:
                line = f'x[index+{self.i2t(item.args[0])}]'
        elif item.type is MULTIPLICATION:
            line = f'{self.i2t(item.args[0])}*{self.i2t(item.args[1])}'
            if isinstance(item.args[0], float) or isinstance(item.args[1], float):
                line = f'(char) ({line})'
        else:
            breakpoint()
            raise Exception(f'unknown symbol {item.type}')
        return line

    def process_branch(self, branch, shift):
        text = ''
        
        if branch.type is CYCLE:
            loop_entry = v.set('loop_entry')
            loop_body = v.set('loop_body')
            loop_end = v.set('loop_end')
            text = f'''
  br label %{loop_entry}
{loop_entry}:
  %{v.set('pointer_value')} = load i64, i64* %{v['pointer_ptr']}, align 8
  %{v.set('data_val_ptr')} = getelementptr inbounds [4000 x i8], [4000 x i8]* %{v['data_ptr']}, i64 0, i64 %{v['pointer_value']}
  %{v.set('data_val')} = load i8, i8* %{v['data_val_ptr']}
  %{v.set('cmp_res')} = icmp eq i8 %{v['data_val']}, 0
  br i1 %{v['cmp_res']}, label %{loop_end}, label %{loop_body}

{loop_body}:
'''
            text += '\n'

        for i in branch.args:
            if i.type is CYCLE:
                text += self.process_branch(i, shift)
                continue
            line = self.i2t(i)
            text += ' ' * shift + line + '\n'
        if branch.type is CYCLE:
            text += f'''
  br label %{loop_entry}
{loop_end}:\n'''
        return text

    def generate(self, ast):
        text = f'''
define i32 @main() #0 {{
  ; uint8_t data[4000];
  %{v.set('data_ptr')} = alloca [4000 x i8], align 16
  %{v.set('pointer_ptr')} = alloca i64, align 4
  ; указатель масива на 0
  ; pointer = 0
  store i64 0, i64* %{v['pointer_ptr']}, align 8

  ; чистим массив
  %{v.set('data_dest')} = bitcast [4000 x i8]* %{v['data_ptr']} to i8*
  call void @llvm.memset.p0i8.i64(i8* %{v['data_dest']}, i8 0, i64 4000, i32 16, i1 false)

'''
        shift = 2
        text += self.process_branch(ast, shift)
        text += f'''
  %{v.set('call_putchar')} = tail call i32 @putchar(i32 13)
  ret i32 0
}}

declare void @llvm.memset.p0i8.i64(i8* nocapture writeonly, i8, i64, i32, i1) #1
declare i32 @putchar(i32) local_unnamed_addr #1
declare i32 @getchar() local_unnamed_addr #1
'''
        return text


class PythonGenerator(CodeGenerator):

    def i2t(self, item):
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
            line = f'p({self.i2t(item.args[0])}, {self.i2t(item.args[1])})'
        elif item.type is '+':
            line = f'add(mem_point, {item.args[0]})'
        elif item.type is '-':
            line = f'add(mem_point, -{item.args[0]})'
        elif item.type is 'clear':
            line = f'{self.i2t(item.args[0])} = 0'
        elif item.type is ',':
            line = 'mem[mem_point] = read()'
        elif item.type is EQUALITY:
            line = f'{self.i2t(item.args[0])}={self.i2t(item.args[1])}'
            # line += ';print(mem[:40]);input();'
        elif item.type is PLUS:
            line = f'(int({self.i2t(item.args[0])}+{self.i2t(item.args[1])})& 0xFF )'
        elif item.type is SUB:
            line = f'(int({self.i2t(item.args[0])}-{self.i2t(item.args[1])})& 0xFF )'
        elif item.type is RELATIVE_POINTER:
            if isinstance(item.args[0], int) and item.args[0] is 0:
                line = f'mem[mem_point]'
            else:
                line = f'mem[mem_point+{self.i2t(item.args[0])}]'
        elif item.type is MULTIPLICATION:
            line = f'{self.i2t(item.args[0])}*{self.i2t(item.args[1])}'
        else:
            breakpoint()
            raise Exception(f'unknown symbol {item.type}')
        return line

    def process_branch(self, branch, shift):
        text = ''
        if branch.type is CYCLE:
            line = 'while mem[mem_point] != 0:'
            text += ' ' * shift + line + '\n'
            shift += 2

        for i in branch.args:
            if i.type is CYCLE:
                text += self.process_branch(i, shift)
                continue
            line = self.i2t(i)
            text += ' ' * shift + line + '\n'
        return text

    def generate(self, ast):
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
        text += self.process_branch(ast, shift)
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
            operanads.append((relative_counter, i))

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
    new_branch.args.append(
        Item(type='clear', args=[Item(type=RELATIVE_POINTER, args=[0])]))
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
    # ast = optimize_ast(ast)
    pp.pprint(ast)
    # java_generator = JavaGenerator()
    # java_code = java_generator.generate(ast)
    # with open('jt/Main.java', 'w') as file:
    #     file.write(java_code)
    # python_generator = PythonGenerator()
    # text = python_generator.generate(ast)
    # with open('prog.py', 'w') as file:
    #     file.write(text)
    # c_generator = CGenerator()
    # text = c_generator.generate(ast)
    # with open('c/main.c', 'w') as file:
    #     file.write(text)
    llvm_generator = LLVMGenerator()
    text = llvm_generator.generate(ast)
    with open('main.ll', 'w') as file:
        file.write(text)
    # print(text)


if __name__ == "__main__":
    main()
