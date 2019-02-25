import argparse
import pprint
pp = pprint.PrettyPrinter(indent=2)

SYMBLS = ['+', '-', '>', '<', '[', ']', '.', ',']
CYCLE = 'cycle'
MULTIPLICATION = 'multi'
EQUALITY = 'eq'
PLUS = 'plus'
SUB = 'substraction'
RELATIVE_POINTER = 'rpoint'
UNWIND = 'unwind'


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

def i2t(item):
    # item to text
    line = ''
    if isinstance(item, int):
        line = str(item)
    elif item.type is '>':
        line = f'mem_point = mem_point + {item.args[0]}'
    elif item.type is '<':
        line = f'mem_point = mem_point - {item.args[0]}'
    elif item.type is '.':
        line = f'p({item.args[0]})'
    elif item.type is '+':
        line = f'add(mem_point, {item.args[0]})'
    elif item.type is '-':
        line = f'add(mem_point, -{item.args[0]})'
    elif item.type is 'clear':
        line = 'mem[mem_point] = 0'
    elif item.type is ',':
        line = 'mem[mem_point] = ord(input(\'>\'))'
    elif item.type is EQUALITY:
        line = f'{i2t(item.args[0])}={i2t(item.args[1])}'
    elif item.type is PLUS:
        line = f'(({i2t(item.args[0])}+{i2t(item.args[1])})& 0xFF )'
    elif item.type is RELATIVE_POINTER:
        line = f'mem[mem_point+({item.args[0]})]'
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
        # print(line)
        text += ' ' * shift + line + '\n'
    return text


def generate_python(ast):
    text = '''mem = [0] * 3000
mem_point = 0
def add(point, val):
    mem[point] = (mem[point] + val) & 0xFF
def p(times):
    print(chr(mem[mem_point]) * times, end=\'\')
'''
    shift = 0
    text += process_branch(ast, shift)
    return text


def remove_repetitions(branch):
    for pos, i in enumerate(branch.args):
        count = 1
        if i is None:
            continue
        if i.type is CYCLE:
            continue
        try:
            while True:
                if branch.args[pos+count].type == i.type:
                    count += 1
                else:
                    break
        except IndexError:
            pass
        branch.args[pos].args = [count]
        if count > 1:
            while count != 1:
                branch.args[pos+count-1] = None
                count -= 1
    return branch

def unwind(branch):
    while True:
        index = -1
        for pos,i in enumerate(branch.args):
            if i.type is UNWIND:
                index = pos
                break;
        if index is -1:
            break;
        item = branch.args.pop(index)
        branch.args[index:index] = item.args
    return branch


def loop_multiplication(branch):
    branch.args = list(filter(lambda x: x is not None, branch.args))
    for i in branch.args:
        if i.type is CYCLE:
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
    operanads = {}
    for i in branch.args:
        if i.type is '>':
            relative_counter += i.args[0]
        elif i.type is '<':
            relative_counter -= i.args[0]
        else:
            if relative_counter not in operanads:
                operanads[relative_counter] = i
            else:
                raise Exception('adding elements')
    new_branch = Item(type='unwind', args=[])
    direction = -1
    if operanads.pop(0).type is '+':
        direction = 1

    for o in operanads.keys():
        if direction is -1:
            item = Item(type=EQUALITY, args=[
                    Item(type=RELATIVE_POINTER, args=[o]),
                    Item(type=PLUS, args=[
                        Item(type=RELATIVE_POINTER, args=[o]),
                        Item(type=MULTIPLICATION, args=[
                            Item(type=RELATIVE_POINTER, args=[0]),
                            operanads[o].args[0]
                        ])
                    ])
                ])
            new_branch.args.append(item)
        else:
            # print(f'mem[point+({o})] += (255 - mem[point]) * {operanads[o].args[0]}')
            # item = Item(type=PLUS, args=[
            #     Item(type=RELATIVE_POINTER, args=[o]),
            #     Item(type=RELATIVE_POINTER, args=[o]),
            #     Item(type=MULTIPLICATION, args=[
            #         Item(type=SUB, args=[255, Item(type=RELATIVE_POINTER, args=[0])]),
            #         operanads[o].args[0]
            #     ])])
            raise Exception('not emplimented')
            new_branch.args.append(item)
        print(operanads[o].type, o, operanads[o].args[0])
    new_branch.args.append(Item(type='clear'))
    print('zero', [i.type for i in new_branch.args], [i.type for i in branch.args])
    # print(branch)
    return new_branch


def optimize_branch(branch):
    if len(branch.args) == 1 and (branch.args[0].type == '-' or branch.args[0].type == '+'):
        return Item(type='clear')
    if len(branch.args) == 0:
        return None
    branch = remove_repetitions(branch)
    branch.args = list(filter(lambda x: x is not None, branch.args))
    # branch = loop_multiplication(branch)
    for pos, i in enumerate(branch.args):
        if i is None:
            continue
        if i.type is CYCLE:
            i = optimize_branch(i)
            branch.args[pos] = i
            continue
    branch = unwind(branch)
    branch.args = list(filter(lambda x: x is not None, branch.args))
    return branch


def optimize_ast(ast):
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
        parent.args.append(item)
    ast = optimize_ast(ast)
    # pp.pprint(vars(ast))
    text = generate_python(ast)
    with open('prog.py', 'w') as file:
        file.write(text)
    # print(text)


if __name__ == "__main__":
    main()
