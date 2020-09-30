import fileinput
import re
from instruction_set import instructions

lookup_table = {}
assembly = []


def toBin(i, n=2, hex=False):
    return format(int(i,16), f"00{n}b") if hex else format(int(i), f"00{n}b")

def to_machine_language(line):
    assembly = line.split()
    hextoint = lambda h: int(h, base=16)
    regstrip = lambda s: re.search('((?<=\$)|(?<=^))([0-3])', s).group(2)

    op = instructions[assembly[0]]
    if op.startswith('001111'):
        appendix = ""
    elif op.startswith('00'): # g-types start with 00
        appendix = toBin(regstrip(assembly[1]))
    elif op.startswith('1'): # j-types start with 1
        appendix = lookup_table[assembly[1]]
    elif op.startswith('01'): # ab-types start with 01
        if assembly[0] == 'init':
            if hextoint(assembly[1]) > 0xF:
                raise Exception("Invalid init immediate")
            appendix = toBin(assembly[1], 4, hex=True)
        else:
            appendix = (toBin(regstrip(assembly[1]))) + toBin(regstrip(assembly[2]))
    return op + appendix


def loop_to_machine_language(line):
    name = re.search('(.*?):', line).group(1)
    return "100" + lookup_table[name]


def build_lookup(line):
    if 'index' not in build_lookup.__dict__:
        build_lookup.index = 0

    if build_lookup.index >= 32:
        raise Exception('ISA does not support more than 32 loops.')

    name = re.search('(.*?):', line).group(1)
    if name in lookup_table:
        raise Exception('Loop assigned several times; causes ambiguity in machine code.')

    lookup_table.update({name: toBin(build_lookup.index, 5)})
    build_lookup.index += 1

def assemble(line):
    if line.startswith('#'):
        return None
    elif ":" in line:
        return loop_to_machine_language(line)
    else:
        return to_machine_language(line)


def assembler(lines):
    global assembly
    for line in lines:
        if line.strip():
            assembly.append(line.rstrip())

    for line in assembly:
        if line.startswith('#'):
            continue
        elif ":" in line:
            build_lookup(line)

    codepairs = {}
    pc = 0
    for line in assembly:
        if assemble(line):
            codepairs.update({pc: [line,assemble(line)]})
            pc += 1
    return codepairs

if __name__ == '__main__':
    # code = (assembler(fileinput.input()))
    code = assembler(open('code.txt'))
    print(lookup_table)
    for pc in code:
        print(pc, code[pc])



