import argparse
import pprint
pp = pprint.PrettyPrinter(indent=2)

SYMBLS = ['+', '-', '>', '<', '[', ']', '.', ',']

def process_branch(branch, shift):
    text = ''
    if branch['type'] is 'cycle':
        line = 'while mem[mem_point] != 0:'
        text += ' ' * shift + line + '\n'
        shift += 2
    
    for i in branch['items']:
        if isinstance(i, dict):
            text += process_branch(i, shift)
            continue
        line = ''
        if i[0] is '>':
            line = f'mem_point = mem_point + {i[1:]}'
        elif i[0] is '<':
            line = f'mem_point = mem_point - {i[1:]}' 
        elif i[0] is '.':
            line = f'p({i[1:]})'
        elif i[0] is '+':
            line = f'add(mem_point, {i[1:]})'
        elif i[0] is '-':
            line = f'add(mem_point, -{i[1:]})'
        elif i[0] is 'c':
            line = 'mem[mem_point] = 0'
        elif i[0] is ',':
            line = 'mem[mem_point] = ord(input(\'>\'))'
        else:
            raise Exception(f'unknown symbol {i}')
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

def optimize_branch(branch):
    if len(branch['items']) == 1 and (branch['items'][0] == '-' or branch['items'][0] == '+') :
        return 'c'
    if len(branch['items']) == 0:
        return None
    for pos, i in enumerate(branch['items']):
        count = 1
        if i is None:
            continue
        if isinstance(i, dict):
            i = optimize_branch(i)
            branch['items'][pos] = i
            continue
        try:
            while True:
                if branch['items'][pos+count] == i:
                    count+=1
                else:
                    break
        except IndexError:
            pass
        branch['items'][pos] = (f'{i}{count}')
        if count >1 :
            while count != 1:
                branch['items'][pos+count-1] = None
                count -=1
    branch['items'] = list(filter(lambda x: x is not None, branch['items']))
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
    ast = {'parent':None, 'items':[], 'type':'Prog'}
    parent = ast
    for item in program:
        if item is '[':
            item = {'parent': parent, 'items':[], 'type':'cycle'}
            parent['items'].append(item)
            parent = item
            continue
        if item is ']':
            parent = parent['parent']
            continue
        parent['items'].append(item)
    ast = optimize_ast(ast)
    pp.pprint(ast)
    text = generate_python(ast)
    with open('test.py', 'w') as file:
        file.write(text)
    # print(text)       

if __name__ == "__main__":
    main()