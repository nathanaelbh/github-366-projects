def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


# for conversion, large values to be displayed in hex format
# the value 255 is not fixed feel free to change it to any other value
# From Piazza
def large_val_limiter(strVal):
    if strVal > 255:
        strVal = hex(strVal)
    return str(strVal)


def dissasembler(inpFileName):
    inputs = []

    inpFile = open(inpFileName, 'r')

    for binInp in inpFile:

        output = ""
        binInp = binInp.replace("\n", "")
        if binInp == "":
            continue
        binInp = str(bin(int(binInp, 16))[2:].zfill(32))

        if binInp[0:6] == "000000" and binInp[26:32] == "100000":  # add
            output = "add"
            output += " $" + str(int(binInp[16:21], 2))  # $rd
            output += ", $" + str(int(binInp[6:11], 2))  # $rs
            output += ", $" + str(int(binInp[11:16], 2))  # $rt

        if binInp[0:6] == "001000":  # addi
            output = "addi"
            output += " $" + str(int(binInp[11:16], 2))  # $rt
            output += ", $" + str(int(binInp[6:11], 2))  # $rs
            imm = twos_comp(int(binInp[16:32], 2), 16)
            imm = large_val_limiter(imm)
            output += ", " + str(imm)  # imm

        if binInp[0:6] == "000000" and binInp[26:32] == "100010":  # add
            output = "sub"
            output += " $" + str(int(binInp[16:21], 2))  # $rd
            output += ", $" + str(int(binInp[6:11], 2))  # $rs
            output += ", $" + str(int(binInp[11:16], 2))  # $rt

        if binInp[0:6] == "001100":  # andi
            output = "andi"
            output += " $" + str(int(binInp[11:16], 2))  # $rt
            output += ", $" + str(int(binInp[6:11], 2))  # $rs
            imm = twos_comp(int(binInp[16:32], 2), 16)
            imm = large_val_limiter(imm)
            output += ", " + str(imm)  # imm

        if binInp[0:6] == "000000" and binInp[26:32] == "101010":  # slt
            output = "slt"
            output += " $" + str(int(binInp[16:21], 2))  # $rd
            output += ", $" + str(int(binInp[6:11], 2))  # $rs
            output += ", $" + str(int(binInp[11:16], 2))  # $rt

        if binInp[0:6] == "100011":  # lw
            output = "lw"
            output += " $" + str(int(binInp[11:16], 2))  # $rt
            imm = twos_comp(int(binInp[16:32], 2), 16)
            imm = large_val_limiter(imm)
            output += ", " + str(imm)  # imm
            output += " ($" + str(int(binInp[6:11], 2)) + ")"  # $rs

        if binInp[0:6] == "101011":  # sw
            output = "sw"
            output += " $" + str(int(binInp[11:16], 2))  # $rt
            imm = twos_comp(int(binInp[16:32], 2), 16)
            imm = large_val_limiter(imm)
            output += ", " + str(imm)  # imm
            output += " ($" + str(int(binInp[6:11], 2)) + ")"  # $rs

        if binInp[0:6] == "000100":  # beq
            output = "beq"
            output += " $" + str(int(binInp[6:11], 2))  # $rs
            output += ", $" + str(int(binInp[11:16], 2))  # $rt
            imm = twos_comp(int(binInp[16:32], 2), 16)
            imm = large_val_limiter(imm)
            output += ", " + str(imm)  # imm

        if binInp[0:6] == "000101":  # bne
            output = "bne"
            output += " $" + str(int(binInp[6:11], 2))  # $rs
            output += ", $" + str(int(binInp[11:16], 2))  # $rt
            imm = twos_comp(int(binInp[16:32], 2), 16)
            imm = large_val_limiter(imm)
            output += ", " + str(imm)  # imm

        if binInp[0:6] == "000010":  # j
            output = "j"
            imm = twos_comp(int(binInp[6:32], 2), 26)
            imm = large_val_limiter(imm)
            output += " " + str(imm)  # imm

        if binInp[0:6] == "000000" and binInp[16:32] == "0000000000011000":  # mult
            output = "mult"
            output += " $" + str(int(binInp[6:11], 2))  # $rs
            output += ", $" + str(int(binInp[11:16], 2))  # $rt

        if binInp[0:16] == "0000000000000000" and binInp[21:32] == "00000010010":  # MFLO
            output = "mflo"
            output += " $" + str(int(binInp[16:21], 2))  # $rs

        output = output.replace(", $", ",")
        output = output.replace(" $", ",")
        output = output.replace("j ", "j,")
        output = output.replace(" ", "")
        output = output.replace("($", ",")
        output = output.replace(")", "")
        output = output.split(",")
        inputs.append(output)

    inpFile.close()
    return inputs


def main():
    print("-------Project 2-------\n")
    inpFileName = "Input.asm"
    print("Enter input file name: use " + inpFileName + "?" + " Enter to accept or type filename: ")
    temp = input()
    if temp != "":
        inpFileName = temp

    outFileName = "OutputP2.txt"
    print("Enter output file name: use " + outFileName + "?" + " Enter to accept or type filename: ")
    temp = input()
    if temp != "":
        outFileName = temp

    outFile = open(outFileName, 'w')
    inputs = dissasembler(inpFileName)
    outputs = []
    reg = [0] * 32
    mem = {}
    for i in range(0x2000, 0x3004, 4):
        mem[hex(i)] = 0
    total = 0
    alu = 0
    jump = 0
    branch = 0
    memory = 0
    other = 0

    pc = 0
    lo = 0
    hi = 0
    pc = 0  # current instruction number, will be needed for jump and branch
    # reg[3] = -3
    # reg[4] = 3

    while pc < len(inputs):
        inst = inputs[pc]

        if inst[0] == "add":  # add
            reg[int(inst[1])] = reg[int(inst[2])] + reg[int(inst[3])]
            pc += 1  # pc = pc+=4
            p = ("{:28} =>${:2} = {:12} =>PC: {:4}".format(str(inst), str(int(inst[1])), str(reg[int(inst[1])]),
                                                           str(pc * 4)))
            alu += 1

        elif inst[0] == "addi":  # addi
            if inst[3][:2] == "0x":
                reg[int(inst[1])] = reg[int(inst[2])] + int(inst[3][2:], 16)
            else:
                reg[int(inst[1])] = reg[int(inst[2])] + int(inst[3])
            pc += 1  # pc = pc+=4
            p = ("{:28} =>${:2} = {:12} =>PC: {:4}".format(str(inst), str(int(inst[1])), str(reg[int(inst[1])]),
                                                           str(pc * 4)))
            alu += 1

        elif inst[0] == "sub":  # sub
            reg[int(inst[1])] = reg[int(inst[2])] - reg[int(inst[3])]
            pc += 1  # pc = pc+=4
            p = ("{:28} =>${:2} = {:12} =>PC: {:4}".format(str(inst), str(int(inst[1])), str(reg[int(inst[1])]),
                                                           str(pc * 4)))
            alu += 1

        elif inst[0] == "andi":  # andi
            if inst[3][:2] == "0x":
                reg[int(inst[1])] = reg[int(inst[2])] & int(inst[3][2:], 16)
            else:
                reg[int(inst[1])] = reg[int(inst[2])] & int(inst[3])
            pc += 1  # pc = pc+=4
            p = ("{:28} =>${:2} = {:12} =>PC: {:4}".format(str(inst), str(int(inst[1])), str(reg[int(inst[1])]),
                                                           str(pc * 4)))
            alu += 1

        elif inst[0] == "slt":  # slt
            if reg[int(inst[2])] < reg[int(inst[3])]:
                reg[int(inst[1])] = 1
            else:
                reg[int(inst[1])] = 0
            pc += 1  # pc = pc+=4
            p = ("{:28} =>${:2} = {:12} =>PC: {:4}".format(str(inst), str(int(inst[1])), str(reg[int(inst[1])]),
                                                           str(pc * 4)))
            other += 1

        elif inst[0] == "lw":  # lw
            if inst[2][:2] == "0x":
                reg[int(inst[1])] = mem[hex(int(reg[int(inst[3])]) + int(inst[2][2:], 16))]

            else:
                reg[int(inst[1])] = mem[hex(int(reg[int(inst[3])]) + int(inst[2]))]
            pc += 1  # pc = pc+=4
            p = ("{:28} =>${:2} = {:12} =>PC: {:4}".format(str(inst), str(int(inst[1])), str(reg[int(inst[1])]),
                                                           str(pc * 4)))
            memory += 1

        elif inst[0] == "sw":  # sw
            pc += 1  # pc = pc+=4
            if inst[2][:2] == "0x":
                mem[hex(int(reg[int(inst[3])]) + int(inst[2][2:], 16))] = reg[int(inst[1])]
                # p = (str(inst) + "  =>[" + str(hex(int(reg[int(inst[3])]) + int(inst[2][2:], 16))) + "] = " + str(
                #     mem[hex(int(reg[int(inst[3])]) + int(inst[2][2:], 16))]) + "  =>PC: " + str(pc * 4))
                p = ("{:28} =>[{:6}] = {:7} =>PC: {:4}".format(str(inst),
                                                               str(hex(int(reg[int(inst[3])]) + int(inst[2][2:], 16))),
                                                               str(
                                                                   mem[hex(
                                                                       int(reg[int(inst[3])]) + int(inst[2][2:], 16))]),
                                                               str(pc * 4)))

            else:
                mem[hex(int(reg[int(inst[3])]) + int(inst[2]))] = reg[int(inst[1])]
                p = (str(inst) + "  =>[" + str(hex(int(reg[int(inst[3])]) + int(inst[2]))) + "] = " + str(
                    mem[hex(int(reg[int(inst[3])]) + int(inst[2]))]) + "  =>PC: " + str(pc * 4))
                p = ("{:28} =>[{:6}] = {:7} =>PC: {:4}".format(str(inst),
                                                               str(hex(int(reg[int(inst[3])]) + int(inst[2]))), str(
                        mem[hex(int(reg[int(inst[3])]) + int(inst[2]))]), str(pc * 4)))
            memory += 1

        elif inst[0] == "mult":  # mult
            result = reg[int(inst[1])] * reg[int(inst[2])]
            temp = bin(result)
            if temp[0] == "-":
                temp = bin(65536 + int(result))[2:].rjust(64, "1")
                hi = int(temp[0:32], 2) - 4294967296
                lo = int(temp[32:64], 2) - 4294967296
            else:
                temp = temp[2:].zfill(32)
                hi = int(temp[0:16], 2)
                lo = int(temp[16:32], 2)
            pc += 1  # pc = pc+=4
            p = (str(inst) + "  =>$ lo = " + str(lo) + "  =>$ hi = " + str(hi) + "  =>PC: " + str(pc * 4))
            alu += 1

        elif inst[0] == "beq":  # beq
            # brach to 1+imm therfore pc=1+imm
            if reg[int(inst[1])] == reg[int(inst[2])]:
                pc += int(inst[3])  # pc = pc+=4
            pc += 1  # pc = pc+=4
            p = ("{:48}  =>PC: {:}".format(str(inst), str(pc * 4)))
            branch += 1

        elif inst[0] == "bne":  # bne
            # brach to 1+imm therfore pc=1+imm
            if reg[int(inst[1])] != reg[int(inst[2])]:
                pc += int(inst[3])  # pc = pc+=4
            pc += 1  # pc = pc+=4
            p = ("{:48}  =>PC: {:}".format(str(inst), str(pc * 4)))
            branch += 1

        elif inst[0] == "j":  # j
            # jump to 1+imm therfore pc=1+imm
            pc = int(inst[1])  # pc = pc+=4
            p = ("{:48}  =>PC: {:}".format(str(inst), str(pc * 4)))
            jump += 1

        elif inst[0] == "mflo":  # bne
            # brach to 1+imm therfore pc=1+imm
            reg[int(inst[1])] = lo
            pc += 1  # pc = pc+=4
            p = ("{:28} =>${:2} = {:12} =>PC: {:4}".format(str(inst), str(int(inst[1])), str(reg[int(inst[1])]),
                                                           str(pc * 4)))
            alu += 1

        print(p)
        outFile.write(p + "\n")

    total = alu + jump + branch + memory + other
    pc *= 4
    print("\n")
    print(" Total: " + str(total))
    print("   ALU: " + str(alu))
    print("  Jump: " + str(jump))
    print("Branch: " + str(branch))
    print("Memory: " + str(memory))
    print(" Other: " + str(other))

    outFile.write("\n")
    outFile.write(" Total: " + str(total))
    outFile.write("\n   ALU: " + str(alu))
    outFile.write("\n  Jump: " + str(jump))
    outFile.write("\nBranch: " + str(branch))
    outFile.write("\nMemory: " + str(memory))
    outFile.write("\n Other: " + str(other))

    print("\nReg #  | Value")
    outFile.write("\nReg #  | Value\n")

    for i in range(32):
        print("${:6}| {}\n".format(i, reg[i]), end='')
        outFile.write("${:6}| {}\n".format(i, reg[i]))
    print("$    {}| {}\n".format("pc", pc), end='')
    print("$    {}| {}\n".format("hi", hi), end='')
    print("$    {}| {}\n".format("lo", lo), end='')
    outFile.write("$    {}| {}\n".format("pc", pc))
    outFile.write("$    {}| {}\n".format("hi", hi))
    outFile.write("$    {}| {}\n".format("lo", lo))

    print("\nAddress |  +0 |  +4 |  +8 |  +c | +10 | +14 | +18 | +1c |")
    outFile.write("\n\nAddress |  +0 |  +4 |  +8 |  +c | +10 | +14 | +18 | +1c |")

    for i in mem:
        if int(i, 16) % 32 == 0:
            print("\n{:8}|".format(i), end='')
            outFile.write("\n{:8}|".format(i))
        print("{:5}|".format(mem[i]), end='')
        outFile.write("{:5}|".format(mem[i]))

    outFile.close()


if __name__ == "__main__":
    main()
