addi $7, $0, 0x2000
addi $6, $7, -3
sub $4, $0, $7
add $8, $4, $6
andi $5, $8, 15
slt $8, $4, $5
sw $8, 0x2008($0)
addi $7, $7, 8
sw $8, -4($7)
lw $8, 0x2004($0)
lw $5, 0($7)
addi $8, $0, 40
addi $7, $0, -13
slt $10, $0, $0
loop: andi $9, $7, 1
beq $9, $0, skip
add $10, $10, $7
sw $7, 0x2000($8)
skip:
# comments supported
addi $8, $8, -4
addi $7, $7, 1
beq $8, $0, out
j loop
bne $8, $0, loop
out:
addi $8, $8, 8208
lw $10, -8($8)
sw $10, 0x2100($0)
