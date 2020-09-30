# Imports
import os
import math
import re
import ctypes
import numpy as np


########### Global Variables ###########
fileBin = []  # Empty Array for Hex->Binary File
fileCont = []  # Empty Array for the file contents
memoryArray = [0] * 1025  # Empty Array for memory contents
opCode = 000000
mode = ""

########### Cache Variables ###########
Hits = 0
Misses = 0

N = 0
S = 0
b = 0

blk_size = 0  # 4 words, 16 bytes
set_id_len = 0  # set id length
total_blk = 0  # total # of blocks
set_offset = 0  # offset
capacity = 0

x = 0x2574

addrbin = bin(x)[2:].zfill(b) #address bin
set_id = addrbin[(b - set_id_len - set_offset):b - set_offset]

if set_id == '':
    set_id = 0

offset = addrbin[(b - set_offset):]
tag = addrbin[0:(b - set_id_len - set_offset)]

word_offset = 0
set_offset = 0
timeVal = 1


# Registers Dictionary
register = {
    0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0, 13:0, 14:0, 15:0, 16:0,
    17:0, 18:0, 19:0, 20:0, 21:0, 22:0, 23:0, 24:0, 25:0, 26:0, 27:0, 28:0, 29:0, 30:0, 31:0,
    'lo':0, 'hi':0, 'PC':0,
}


########### Important Functions ###########
# Updates cache variables
def updatecachevar(N, S, b):
    blk_size = b / 4  # 4 words, 16 bytes
    set_id_len = int(math.log(S, 2))  # set id length
    total_blk = N * S  # total # of blocks
    set_offset = int(math.log(b, 2))  # offset
    capacity = total_blk * b

# 2's Complement
def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

# Hex to Binary Conversion
def hexToBin(arrayData):
  global fileBin
  for string in arrayData:
    temp = bin(int(string, 16))[2:]
    temp = temp.zfill(32)
    fileBin.append(temp)

# Decimal to Hex Conversion (2's Complement)(8-digit Hex)
OFFSET = 1 << 32
MASK = OFFSET - 1
def int2hex(num):
    hexNum = '%08x' % (num + OFFSET & MASK)
    bytes = []
    for i in range(0,1):
        bytes.append(hexNum[i * 2: i * 2 + 8])
    item = bytes[::-1]
    item = str(item[0])
    return item

# Decimal to Hex Conversion (2's Complement)(2-digit Hex)
def _int2hex(num):
    hex = '%08x' % (num + OFFSET & MASK)
    bytes = []
    for i in range(0, 4):
        bytes.append('0x' + hex[i * 2: i * 2 + 2])
    bytes[::-1]
    item = bytes[3]
    return item

def hex2int(hexstr):
    value = int(hexstr,16)
    if value & (1 << (32-1)):
        value -= 1 << 32
    return value


# Takes in N, S, b values of the cache configurations and does the necessary cache calculations
def decipher():
    global fileBin, Hits, Misses, N, S, b, opCode, mode, InstructionCount, memoryArray, time, timeVal
    functName = ""
    functType = ""
    binary = fileBin[int(register['PC']/4)]
    if fileBin[int(register['PC']/4)][0:6] == "000000":
        functType = "r"
        opCode = fileBin[int(register['PC']/4)][26:32]
    elif fileBin[int(register['PC']/4)][0:6] != "000010":
        opCode = fileBin[int(register['PC']/4)][0:6]
        functType = "i"
    elif fileBin[int(register['PC']/4)][0:6] == "000010":
        functType = "j"
    else:
        print("You shouldn't be here")

    # R-Type Calculations
    if functType == "r":
        rs = int(binary[6:11], 2)
        rt = int(binary[11:16], 2)
        rd = int(binary[16:21], 2)

        if opCode == "100000": # add
            functName = "add"
            register[rd] = register[rs] + register[rt]

        if opCode == "100001": # addu
            functName = "addu"
            register[rd] = register[rs] + register[rt]

        if opCode == "100010": # sub
            functName = "sub"
            register[rd] = register[rs] - register[rt]

        if opCode == "011000": # mult
            functName ="mult"
            product = register[rs] * register[rt]
            if (product >= -4294967295) and (product < 4294967295):
                register['lo'] = product  # lo
                register['hi'] = 0  # hi
            else:
                register['hi'] = product // 4294967295  # hi
                register['lo'] = product - (register['hi'] * 4294967295)  # lo

        if opCode == "011010": # div
            functName = "div"
            tempS = register[rs]
            tempT = register[rt]
            if (tempS < 0) or (tempT < 0):
                register['lo'] = (abs(register[rs]) // abs(register[rt])) * -1
            else:
                register['lo'] = register[rs] // register[rt]
            register['hi'] = abs(register[rs] % register[rt])
        if opCode == "101010": # slt
            functName = "slt"
            if int(register[rs]) < int(register[rt]):
                register[rd] = 1
            else:
                register[rd] = 0
        if opCode == "010010": # mflo
            functName = "mflo"
            tempReg = int(binary[16:21], 2)
            register[tempReg] = register['lo']
        if opCode == "010000": # mfhi
            functName = "mfhi"
            tempReg = int(binary[16:21], 2)
            register[tempReg] = register['hi']

    # I-Type Calculations
    elif functType == "i":
        rs = int(binary[6:11], 2)
        rt = int(binary[11:16], 2)
        if binary[16] == "1":  # If true, then imm is negative
            imm = (int(65536) - int(binary[16:32], 2)) * -1
        else:
            imm = int(binary[16:32], 2)
        if opCode == "001000": # addi
            functName = "addi"
            register[rt] = register[rs] + imm

        if opCode == "100011": # lw
            functName = "lw"
            if int(imm + register[rs] - int(8192)) == 0:
                register[rt] = memoryArray[0]
            else:
                register[rt] = memoryArray[int(((imm + register[rs]) - int(8192)) / 4)]
            cache_sim(imm+register[rs])

        if opCode == "101011": # sw
            functName = "sw"
            if imm + register[rs] == 8192:
                memoryArray[0] = register[rt]
            else:
                destAddress = int(((imm + register[rs]) - int(8192)) / 4)
                memoryArray[destAddress] = register[rt]
            cache_sim(imm+register[rs])

        if opCode == "100000": # lb
            functName = "lb"
            if int(imm + register[rs] - int(8192)) == 0:
                tempReg = memoryArray[0]
                if memoryArray[0] == 0:
                    register[rt] = 0
                else:
                    register[rt] = str(tempReg)[6:8]
            else:
                tempReg = memoryArray[int(((imm + register[rs]) - int(8192))/4)]
                tempReg = int2hex(tempReg)  # tempReg is now hex
                whichByte = (imm + register[rs] - int(8192)) % 4
                if whichByte == 0:  # First Byte
                    if (str(tempReg)[6:8] == "00"):
                        register[rt] = 0
                    else:
                        register[rt] = ctypes.c_int8(int(str(bin(int(tempReg, 16)))[2:].zfill(32)[24:], 2)).value
                elif whichByte == 1:  # Second Byte
                    if (int(str(tempReg)[4:6], 16) == "00"):
                        register[rt] = 0
                    else:
                        item = str(ctypes.c_int8(int(str(bin(int(tempReg, 16)))[2:].zfill(32)[16:24], 2)).value)
                        register[rt] = (int(item))
                elif whichByte == 2:  # Third Byte
                    if (int(str(tempReg)[2:4], 16) == "00"):
                        register[rt] = 0
                    else:
                        register[rt] = ctypes.c_int8(int(str(bin(int(tempReg, 16)))[2:].zfill(32)[8:16], 2)).value
                elif whichByte == 3:  # Fourth Byte
                    if (int(str(tempReg)[0:2], 16) == "00"):
                        register[rt] = 0
                    else:
                        register[rt] = ctypes.c_int8(int(str(bin(int(tempReg, 16)))[2:].zfill(32)[0:8], 2)).value
            cache_sim(imm+register[rs])
        if opCode == "101000": # sb
            functName = "sb"
            if imm + register[rs] == 8192:  # This should not be access right now | ignored
                tempReg = register[rt]
                tempNum = hex(memoryArray[0])[2:].zfill(8)
            else:
                destAddress = int(((imm + register[rs]) - int(8192))/4)  # Destination Address in Array
                whichByte = (imm + register[rs] - int(8192)) % 4
                tempData = int2hex(memoryArray[destAddress])  # It is now 8-digit hex
                tempData = str(tempData)
                byteData = _int2hex(register[rt])  # register is now 2-digit hex
                byteData = str(byteData)[2:]
                if whichByte == 0:  # First Byte
                    subStr06 = tempData[0:6]
                    subStr08 = subStr06 + byteData
                    memoryArray[destAddress] = hex2int(subStr08)
                if whichByte == 1:  # Second Byte
                    subStr04 = tempData[0:4]
                    subStr68 = tempData[6:8]
                    subStr08 = subStr04 + byteData + subStr68
                    memoryArray[destAddress] = hex2int(subStr08)
                if whichByte == 2:  # Third Byte
                    subStr02 = tempData[0:2]
                    subStr48 = tempData[4:8]
                    subStr08 = subStr02 + byteData + subStr48
                    memoryArray[destAddress] = hex2int(subStr08)
                if whichByte == 3:  # Fourth Byte
                    subStr28 = tempData[2:]
                    subStr08 = byteData + subStr28
                    memoryArray[destAddress] = hex2int(subStr08)
            cache_sim(imm+register[rs])
        if opCode == "000100": # beq
            functName = "beq"
            if register[rs] == register[rt]:  # Satisfies condition of the branch
                if imm > 0:  # Forward Jump
                    branchJump = register['PC'] + imm * 4
                elif imm < 0:  # Backward Jump
                    branchJump = register['PC'] - (-imm * 4)
                else:
                    branchJump = register['PC']
                register['PC'] = branchJump
        if opCode == "000101": # bne
            functName = "bne"
            if register[rs] != register[rt]:  # Satisfies condition of the branch
                if imm > 0:  # Forward Jump
                    branchJump = register['PC'] + imm * 4
                elif imm < 0:  # Backward Jump
                    branchJump = register['PC'] - (-imm * 4)
                else:
                    branchJump = register['PC']
                register['PC'] = branchJump
        if opCode == "001101": # ori
            functName = "ori"
            compReg = int(register[rs])
            compImm = int(imm)
            register[rt] = compReg | compImm


# Cache simulator function
def cache_sim(x):
    global Misses, Hits, timeVal, time, Cache, Valid
    addrbin = bin(x)[2:].zfill(b)  # address bin
    set_id = addrbin[(b - set_id_len - set_offset):b - set_offset]

    if set_id == '':
        set_id = 0

    offset = addrbin[(b - set_offset):]
    tag = addrbin[0:(b - set_id_len - set_offset)]

    if(S==1):
        set_id = int(set_id)
    else:
        set_id = int(set_id, 2)

    if (mode == 'd'):
        print('Address:', hex(int(addrbin, 2)), '       Tag:', hex(int(tag, 2)), '      Set:', str(set_id), '       Offset:', str(offset))
    if (Valid[set_id][0] == 'INVALID'):
        Misses += 1
        time[set_id][0] = timeVal
        timeVal += 1
        Cache[set_id][0][0] = str(tag)
        Valid[set_id][0] = 'VALID'
        if (mode == 'd'):
            print("Cache missed due to valid bit = 0")
            print("Cache Log:    Updated Set", set_id, "  Way 0:", "  Now VALID with TAG:", hex(int(Cache[set_id][0][0], 2)))
            print("Current Misses:", Misses, "      Hits:", Hits)
    else:  # Valid, now check if tag matches
        flag = 0
        for i in range(N):
            temp_tag = Cache[set_id][i][0]
            if (temp_tag == tag):  # Cache hit
                time[set_id][i] = timeVal   #Sets the time variables
                timeVal += 1
                Hits += 1
                if (mode == 'd'):
                    print("Cache hit")
                    print("Cache Log:    Set remains the same   Set", set_id, "  Way", i," TAG:",hex(int(Cache[set_id][i][0], 2)))
                    print("Current Misses:", Misses, "      Hits:", Hits)
                flag = 1
                break

        if flag == 0:  # Tag doesnt match, cache miss
            Misses += 1

            # LRU, check for smallest time value in time array
            temp = min(time[set_id])
            for i in range(N):
                if temp == time[set_id][i]:
                    temp = i
                    break

            # Replaces the least used way out of the ways.
            Cache[set_id][temp][0] = str(tag)

            #Sets valid and increments time variable to keep track of use.
            time[set_id][temp] = timeVal
            Valid[set_id][temp] = 'VALID'
            timeVal += 1
            if (mode == 'd'):
                print("Cache missed due to tag mismatch")
                print("Cache Log:    Updated Set", set_id, "  Way", temp, "  Now VALID with TAG:", hex(int(Cache[set_id][temp][0], 2)))
                print("Current Misses:", Misses, "      Hits:", Hits)
    if mode == "d":
        print("")


########### M A I N ###########
#### Cache Configuration Selection ####
print("Select Cache Configuration: '1' (N = 1, S = 1, b = 32) | '2' (N = 1, S = 4, b = 128) '3' (N = 2, S = 4, b = 64) | '4' (N = 4, S = 1, b = 64) | '5' Custom N, S, b")
configMode = input("Enter a number: ")  # IMPORTANT VARIABLE
while (int(configMode) > 5) or (int(configMode) < 1):
    print("Invalid Cache Configuration")
    configMode = input("Enter a number(1-5): ")

# Setting Corresponding N, S, b values based on the selection above
if configMode == "1":
    N = 1
    S = 1
    b = 32
elif configMode == "2":
    N = 1
    S = 4
    b = 124
elif configMode == "3":
    N = 2
    S = 4
    b = 64
elif configMode == "4":
    N = 4
    S = 1
    b = 64
elif configMode == "5":
    N = input("Enter a Value for Number of Ways (N): ")
    S = input("Enter a Value for Number of Sets (S): ")
    b = input("Enter a Value for size of block in bytes (b): ")
    N = int(N)
    S = int(S)
    b = int(b)
else:
    print("Should not be here bud")

blk_size = int(b/16)  # 4 words, 16 bytes
set_id_len = int(math.log(S, 2)) #set id length
total_blk = N * S #total # of blocks
set_offset = int(math.log(b, 2)) #offset
capacity = total_blk * b

time = np.array([[0]*N]*S)
Valid = np.array([['INVALID']*N]*S)   # valid bits and tag data
Tag = np.array([[0]*N]*S)
blck = [None for i in range(b)]
Cache = np.array([[blck]*N]*S)

#### Program Mode Selection ####
mode = input("Enter 'd' for Detailed Display Mode or 'f' for Fast Mode: ")
while mode != 'd' and mode != 'f':
    print("Invalid Mode")
    mode = input("Enter 'd' for Detailed Display Mode or 'f' for Fast Mode: ")

# Obtaining and storing file info (Hex) into fileCont
file = input("Enter a text file name: ")
with open(file, "r") as fr:
    for line in fr:
        fileCont.append(line.strip("\n"))
fr.close()

# Converting Hex Array to Binary Array
hexToBin(fileCont)

# Obtaining the maximum PC of the file
maxPC = len(fileCont) * 4

#### Main Loop ####
# Loop until PC reaches end
while register['PC'] < maxPC:
    decipher()
    register['PC'] += 4

print("")
print("CACHE---------------------------------------------")
for i in range(S):
    for j in range(N):
        print("Set:", i, " Way: ", j, end='')
        if(Valid[i][j] == "VALID"):
            print("     VALID,      TAG:", hex(int(Cache[i][j][0], 2)))
        else:
            print("     INVALID,    TAG: 0x00")
print("")
print("Misses", Misses, "       Hits:", Hits, "         Hit Rate:", Hits/(Misses+Hits))