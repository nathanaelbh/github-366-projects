addi $1, $0, 2 # A [A = $1] [CHANGE HERE]
addi $2, $0, 13 # B [B = $2] [CHANGE HERE]
addi $3, $0, 200 # Sample points to generate [CHANGE FOR LARGER OR SMALLER SAMPLE SIZE]
addi $4, $0, 0 # Counter which starts at 0 and counts the elements
addi $7, $0, 0 # x-value
addi $8, $0, 0 # y-value
addi $9, $0, 1 # STATIONARY VARIABLE
addi $10, $0, 0x2020 # x[i] starting location address
addi $11, $0, 0x2420 # y[i] starting location address
addi $12, $0, 0 # Counter to reset to 0 each time
addi $13, $0, 0 # Total Counter for how many iterations [COMPARISON INTEGER]
addi $15, $0, 0x2820 # Address start location of C[i]
addi $26, $0, 0
addi $27, $0, 0
addi $30, $0, 0 # slt sets

main:
addi $12, $0, 0
addi $13, $13, 1
beq $4, $3, partB
bne $4, $3, xValR

xValR: #RIGHT
addi $7, $7, 1 # Add one to X
sw $7, 0($10)
sw $8, 0($11)
addi $10, $10, 4
addi $11, $11, 4
addi $4, $4, 1 # counter for total inputted data
addi $12, $12, 1 # Loop counter
beq $4, $3, partB
bne $12, $13, xValR

addi $12, $0, 0
yValU: #UP
addi $8, $8, 1 # Add one to Y
sw $7, 0($10)
sw $8, 0($11)
addi $10, $10, 4
addi $11, $11, 4
addi $4, $4, 1
addi $12, $12, 1
beq $4, $3, partB
bne $12, $13, yValU

addi $13, $13, 1
addi $12, $0, 0
xValL: #LEFT (NEGATIVE)
addi $7, $7, -1 # Subtract one from X
sw $7, 0($10)
sw $8, 0,($11)
addi $10, $10, 4
addi $11, $11, 4
addi $4, $4, 1
addi $12, $12, 1
beq $4, $3, partB
bne $12, $13, xValL

addi $12, $0, 0
yValD: #DOWN (NEGATIVE)
addi $8, $8, -1 # Subtract one from Y
sw $7, 0($10)
sw $8, 0($11)
addi $10, $10, 4
addi $11, $11, 4
addi $4, $4, 1
addi $12, $12, 1
beq $4, $3, partB
bne $12, $13, yValD
beq $12, $13, main


partB: # This loop will be accessed AFTER the spiral is created
addi $10, $0, 0x2020 # x[i] starting location address [RESET]
addi $11, $0, 0x2420 # y[i] starting location address [RESET]
addi $4, $0, 0 # Resetting element counter to 0

classificationLoop:
addi $16, $0, 0 # A * x[i] Sum Register [SUM OF BOTH AX + BY IS STORED HERE AT THE END]
addi $17, $0, 0 # B * y[i] Sum Register
lw $16, 0($10) # AX
mult $16, $1 # AX
mflo $16 # AX
lw $17, 0($11) # BY
mult $17, $2 # BY
mflo $17 # BY
add $16, $16, $17
addi $10, $10, 4
addi $11, $11, 4
beq $4, $3, partC
slt $30, $16, $0 # $30 = 1 IF $T1 < $T2, ELSE $30 = 0
beq $30, $0, resultGTET0
beq $30, $9, resultLT0

resultGTET0: # When Ax + By >= 0
addi $18, $0, 1 # c[i] is 1
sw $18, 0($15)
#sw $16, 0($15) # DEBUG
addi $15, $15, 4
addi $4, $4, 1 # increment n elements
beq $18, $18, classificationLoop

resultLT0: # When Ax + By < 0
addi $18, $0, -1 # c[i] is -1
sw $18, 0($15)
#sw $16, 0($15) # DEBUG
addi $15, $15, 4
addi $4, $4, 1 # increment n elements
beq $18, $18, classificationLoop


partC: # Perceptron Algorithm
addi $10, $0, 0x2020 # x[i] starting location address [RESET]
addi $11, $0, 0x2420 # y[i] starting location address [RESET]
addi $15, $0, 0x2820 # Address start location of C[i] [RESET]
addi $4, $0, 0 # Reset counter
addi $16, $0, 0 # Ax Multiplication index
addi $17, $0, 0 # Bx Multiplication index
addi $19, $0, 0 # small c = sign(f)
addi $20, $0, 1 # current A
addi $21, $0, 1 # current B
addi $22, $0, 1 # next A
addi $23, $0, 1 # next B
addi $25, $0, 0 # update number [C - c]

algorithm:
lw $16, 0($10) # AX
mult $16, $20 # AX
mflo $16 # AX
lw $17, 0($11) # BX
mult $17, $21 # BX
mflo $17 # BX
add $24, $16, $17 # f = ax+bx
beq $4, $3, finalStore
slt $30, $24, $0 # $30 = 1 IF $T1 < $T2, ELSE $30 = 0
beq $30, $0, currentGTET0
beq $30, $9, currentLT0

currentGTET0:
addi $18, $0, 1 # c[i] = 1
lw $25, 0($15)
sub $25, $25, $18 # C - c
addi $18, $0, 2
div $25, $18 # (C - c) / 2
mflo $25
lw $7, 0($10) # load X-value
mult $25, $7 # ((C - c) / 2) * X Value
mflo $26
add $22, $26, $20 # next A
lw $8, 0($11)
mult $25, $8
mflo $27
add $23, $27, $21 # next B
add $20, $22, $0 # current A <- next A
add $21, $23, $0 # current B <- next B
addi $15, $15, 4
addi $10, $10, 4
addi $11, $11, 4
addi $4, $4, 1 # increment n elements
beq $4, $3, finalStore
addi $18, $0, 1
beq $18, $9, algorithm

currentLT0:
addi $18, $0, -1 # c[i] = -1
lw $25, 0($15)
sub $25, $25, $18 # C - c
addi $18, $0, 2
div $25, $18 # (C - c) / 2
mflo $25
lw $7, 0($10) # load X-value
mult $25, $7
mflo $26
add $22, $26, $20 # next A
lw $8, 0($11)
mult $25, $8
mflo $27
add $23, $27, $21 # next B
add $20, $22, $0 # current A <- next A
add $21, $23, $0 # current B <- next B
addi $15, $15, 4
addi $10, $10, 4
addi $11, $11, 4
addi $4, $4, 1 # increment n elements
beq $4, $3, finalStore
addi $18, $0, -1
beq $18, $18, algorithm

finalStore:
sw $22, 0x2000($0)
sw $23, 0x2004($0)
#DONE