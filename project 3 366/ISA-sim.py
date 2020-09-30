import fileinput
import sys
from instruction_set import instructions
from Assembler import assembler

instructions = {v: k for k, v in instructions.items()}  # invert the instructions

instruction, machine_code, gg, aa, bb, jjjjj = [""] * 6
pc = 0
cs = []

dynamic_instruction_count = 0

def reg(n):
    return "$" + str(int(n,2))

def binstrip(i, n=4):
    return format(int(i), f'#00{n+2}b')[2:]

lookup_table = {}
for x in range(32):
    lookup_table.update({binstrip(x,5): 0})

registers = {}
for x in range(4):
    registers.update({f"${x}": 0})
registers.update({'result': 0, 'return': 0, 'counter': 0, 'init': 0, 'status':0})


data_memory = {}
for x in range(0, 2304):
    data_memory.update({x: 0})

code = {}
argv = {}


def set_machine_code(code):
    global machine_code
    if len(code) != 8:
        raise Exception("Invalid length of machine code.")
    machine_code = code


def set_pc(n=0):
    global pc
    pc = int(n)


def get_pc():
    return pc


def increment_pc(n=1):
    global pc
    pc += n


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val  # return positive value as is


class ShowUpdate(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargv):
        global dynamic_instruction_count

        if (argv["-showcode"]):
            old_registers = dict(registers)
            old_pc = int(get_pc())
            old_memory = dict(data_memory)
        increment_pc()
        # show_ab()
        self.f()
        dynamic_instruction_count += 1
        if(argv["-showcode"]):
            if get_pc() >= 61:
                for key in registers.keys():
                    if registers[key] != old_registers[key]:
                        print(f"\t\t{key}: {old_registers[key]} -> {registers[key]}")
                for key in data_memory.keys():
                    if data_memory[key] != old_memory[key]:
                        print(f"\t\tmem[{key}]: {old_memory[key]} -> {data_memory[key]}")
                if old_pc != get_pc():
                    print(f"\t\tpc: {'0x' + format(old_pc, '004X')} -> {'0x' + format(get_pc(), '004X')}")
                    print()


def set_words():
    global jjjjj, aa, bb, gg, instruction

    jjjjj = machine_code[-5:]
    aa = machine_code[-4:-2]
    bb = machine_code[-2:]
    gg = machine_code[-2:]

    instruction = None
    for encoding in instructions:
        if machine_code.startswith(encoding):
            instruction = globals()[instructions[encoding]]
            break
    if not instruction:
        raise Exception("Instruction not found")


@ShowUpdate
def init():
    global registers

    registers['init'] = registers['init'] | int((aa+bb),2) << 4 * registers['counter']
    if registers['counter'] == 3:
        registers['result'] = twos_comp(registers['init'], 16)
        registers['counter'] = 0
        registers['init'] = 0
    else:
        registers['counter'] = registers['counter'] + 1


@ShowUpdate
def set():
    global registers, data_memory, lookup_table
    registers[reg(gg)] = registers['result']

@ShowUpdate
def add1():
    global registers, data_memory, lookup_table
    registers[reg(gg)] += 1

@ShowUpdate
def sub1():
    global registers, data_memory, lookup_table
    registers[reg(gg)] -= 1

@ShowUpdate
def add1c():
    global registers, data_memory, lookup_table
    data_memory[int(gg,2)+8] += 1

@ShowUpdate
def hold():
    global registers
    registers['result'] = registers['$0']

@ShowUpdate
def addback():
    global registers
    registers['$0'] += registers['result']


@ShowUpdate
def seqc():
    global registers, data_memory, lookup_table
    if data_memory[int(gg,2)+4] == data_memory[int(gg,2)+8]:
        registers['status'] = 1
        data_memory[int(gg,2)+4] = 0
    else:
        registers['status'] = 0
        data_memory[int(gg,2)+4] += 1

@ShowUpdate
def swinc():
    global registers, data_memory
    data_memory[registers[reg(bb)]] = registers[reg(aa)]
    registers[reg(bb)] += 1

@ShowUpdate
def lwinc():
    global registers
    registers['$0'] = data_memory[registers[reg(gg)]]
    registers[reg(gg)] += 1

@ShowUpdate
def lwmult():
    global registers
    registers['$0'] *= data_memory[registers[reg(gg)]]

@ShowUpdate
def lwmultinc():
    global registers
    registers['$0'] *= data_memory[registers[reg(gg)]]
    registers[reg(gg)] += 1

@ShowUpdate
def lwprev():
    global registers
    registers['$0'] = data_memory[registers[reg(gg)]-1]

@ShowUpdate
def swprev():
    global registers
    data_memory[registers[reg(gg)]-1] = registers['$0']

@ShowUpdate
def swf():
    global data_memory
    data_memory[int(gg,2)] = registers['$0']


@ShowUpdate
def lwf():
    global registers
    registers['$0'] = data_memory[int(gg,2)]


@ShowUpdate
def lwfaddreg():
    global registers
    registers['$0'] = data_memory[int(gg,2)] + registers['$0']

@ShowUpdate
def lwfsubreg():
    global registers
    registers['$0'] = data_memory[int(gg,2)] - registers['$0']


@ShowUpdate
def add():
    global registers
    registers[reg(aa)] += registers[reg(bb)]


@ShowUpdate
def sub():
    global registers
    registers[reg(aa)] -= registers[reg(bb)]


@ShowUpdate
def mult():
    global registers
    registers[reg(aa)] *= registers[reg(bb)]


def loop():
    pass


@ShowUpdate
def jif():
    global registers
    if registers['status']:
        set_pc(lookup_table[jjjjj])


@ShowUpdate
def j():
    set_pc(lookup_table[jjjjj])


@ShowUpdate
def slt():
    global registers
    registers['status'] = 1 if registers[reg(gg)] < 0 else 0

@ShowUpdate
def snotneg():
    global registers
    registers['status'] = 0 if registers[reg(gg)] < 0 else 1

@ShowUpdate
def snotneg():
    global registers
    registers['status'] = 1 if registers[reg(gg)] >= 0 else 0

@ShowUpdate
def negpos():
    global registers
    registers['$0'] = -1 if registers['$0'] < 0 else 1

def first_pass():
    global dynamic_instruction_count
    for pc in code.keys():
        if code[pc][1].startswith('100'):
            dynamic_instruction_count += 1
            lookup_table.update({code[pc][1][3:]: pc+1})
    if argv["-showlookup"]:
        print(lookup_table)


def second_pass():
    set_pc()
    max_pc = max(code.keys())
    while get_pc() <= max_pc:
        set_machine_code(code[get_pc()][1])
        set_words()
        if argv["-showcode"]:
                print("{:<16}".format(pc) + "{:<16}".format(str(code[pc])))
        if instruction == loop:
            increment_pc()
            continue
        instruction()


def register_contents():
    print("{:>10}".format("Register") + "{:>10}".format("Value"))
    for key in registers.keys():
        print("{:>10}".format(key) + "{:>10}".format(registers[key]))
    print("{:>10}".format("PC") + "{:>10}".format(get_pc()))

def memory_contents():
    string = "{:>16}".format(f"Base Address")
    for n in range(0,8):
        string += "{:>16}".format(f"[+{n}]")
    print(string)
    for x in range(1024,1124,8):
        string = "{:>16}".format(f"[{x}]")
        for y in range(0, 8):
            string += "{:>16}".format(f"{data_memory[x+y]}")
        print(string)

def counter_contents():
    for n in range(0,4):
        print(f"Data[{n+4}]: {data_memory[n+4]}, Data[{n+8}]: {data_memory[n+8]}")
    print()

def fast_mem():
    for n in range(0,4):
        print(f"Data[{n}]: {data_memory[n]}")

def show_ab():
    for n in range(0,2):
        print(f"Data[{n}]: {data_memory[n]}")

def coordinate_pairs():
    string = "{:>16}".format(f"Base Coords")
    for n in range(0,8):
        string += "{:>16}".format(f"[+{n}]")
    print(string)
    for x in range(0,100,8):
        string = "{:>16}".format(f"[{256+x},{512+x},]")
        for y in range(0,8):
            string += "{:>16}".format("{:<4}".format(f"[{data_memory[256+x+y]},") +
                                      "{:>4}".format(f"{data_memory[512+x+y]}]"))
        print(string)
    print()

def showinstructioncount():
    print(f"Dynamic instruction count:{dynamic_instruction_count}")



if __name__ == '__main__':
    code = []
    argv = {"-showcode": True, "-showmem": False, "-showcounter": False, "-showfmem": False,
            "-showreg": False, "-showcoord": True, "-showlookup": False, "-showinstructioncount": True}

    for arg in sys.argv[1:]:
        if arg.split("=")[0] in argv:
            try:
                argv[arg.split("=")[0]] = False if arg.split("=")[1].lower() == 'false' else True
            except:
                argv[arg.split("=")[0]] = True

    sys.argv.clear()

    
    code = assembler(fileinput.input())
    first_pass()
    second_pass()

    if(argv["-showcoord"]):
        coordinate_pairs()
    if(argv["-showmem"]):
        memory_contents()
    if (argv["-showreg"]):
        register_contents()
    if (argv["-showcounter"]):
        counter_contents()
    if (argv["-showfmem"]):
        fast_mem()
    if (argv["-showinstructioncount"]):
        showinstructioncount()

    print(cs)
