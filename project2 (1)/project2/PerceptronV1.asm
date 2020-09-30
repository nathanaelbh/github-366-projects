addi $1, $0, 5 # A 
addi $2, $0, -6 # B
addi $3, $0, 100 # n
addi $4, $0, 0x2020 # X[n]
addi $5, $0, 0x2420 # Y[n]
addi $6, $0, 0 # X position
addi $7, $0, 0 # Y position
addi $8, $0, 1 # current step
addi $12, $12, 0 # step counter
add  $11, $0, $3 # N counter
right: addi $6, $6, 1 # X++
sw   $6, 0($4)
sw   $7, 0($5)
addi $4, $4, 4 # Xmemory +4
addi $5, $5, 4 # Ymemory +4
addi $11, $11, -1 # N--
beq  $11, $0, exitA
addi $12, $12, 1 
bne  $12, $8, right # loop until step# times
addi $12, $0, 0
up: addi $7, $7, 1 # Y+1
sw   $6, 0($4)
sw   $7, 0($5)
addi $4, $4, 4 # Xmemory +4
addi $5, $5, 4 # Ymemory +4
addi $11, $11, -1 # N--
beq  $11, $0, exitA
addi $12, $12, 1
bne  $12, $8, up # loop until step# times
addi $12, $0, 0
addi $8, $8, 1 # step++
left: addi $6, $6, -1 # X--
sw   $6, 0($4)
sw   $7, 0($5)
addi $4, $4, 4 # Xmemory +4
addi $5, $5, 4 # Ymemory +4
addi $11, $11, -1 # N--
beq  $11, $0, exitA
addi $12, $12, 1
bne  $12, $8, left # loop until step# times
addi $12, $0, 0
down:addi $7, $7, -1 # Y--
sw   $6, 0($4)
sw   $7, 0($5)
addi $4, $4, 4 # Xmemory +4
addi $5, $5, 4 # Ymemory +4
addi $11, $11, -1 # N--
beq  $11, $0, exitA
addi $12, $12, 1
bne  $12, $8, down # loop until step# times
addi $8, $8, 1 # step++
addi $12, $0, 0
j right
exitA:addi $4, $0, 0x2020 # X[n]
addi $5, $0, 0x2420 # Y[n]
addi $6, $0, 0 # X position
addi $7, $0, 0 # Y position
addi $8, $0, 0x2820 # classification result
add $11, $0, $3 # N counter
partB:lw   $6, 0($4)
lw   $7, 0($5)
mult $6, $1 # A * x[i]
mflo $9
mult $7, $2 # B * y[i]
mflo $10
add  $9, $9, $10 # A * x[i] + B * y[i] 
slt  $10, $9, $0
beq  $10, $0, pos
neg:addi $9, $0, -1
sw   $9, 0($8)
addi $8, $8, 4
j skip
pos:addi $9, $0, 1
sw   $9, 0($8)
addi $8, $8, 4
skip:addi $4, $4, 4 # Xmemory +4
addi $5, $5, 4 # Ymemory +4
addi $11, $11, -1 # N--
beq  $11, $0, exitB
j partB
exitB:addi $1, $0, 1 # A = 1
addi $2, $0, 1 # B = 1
add  $11, $0, $3 # N counter
addi $4, $0, 0x2020 # X[n]
addi $5, $0, 0x2420 # Y[n]
addi $6, $0, 0 # X position
addi $7, $0, 0 # Y position
addi $8, $0, 0x2820 # classification result
partC:lw   $6, 0($4) # X
lw   $7, 0($5) # Y
lw   $3, 0($8) # C
mult $6, $1 # A * x[i]
mflo $9
mult $7, $2 # B * y[i]
mflo $10
add  $9, $9, $10 # A * x[i] + B * y[i] 
slt $10, $9, $0
beq  $10, $0, pos2
neg2:addi $9, $0, -1
beq  $9, $3, skip2
add  $1, $1, $6 # a= a+xi
add  $2, $2, $7 # b = b+yi
j skip2
pos2:addi $9, $0, 1
beq  $9, $3, skip2
sub  $1, $1, $6 # a= a+xi
sub  $2, $2, $7 # b = b+yi
skip2:addi $4, $4, 4 # go to next X val regester
addi $5, $5, 4
addi $8, $8, 4
addi $11, $11, -1 # N--
beq  $11, $0, exitC
j partC
exitC:addi $4, $0, 0x2000
addi $5, $0, 0x2004
sw   $1, 0($4)
sw   $2, 0($5)





















