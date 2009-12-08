ori $r1, $r0, 5
ori $r2, $r0, 0
ori $r3, $r0, 0
ori $r4, $r0, 0
ori $r5, $r0, 1

addi $r2, $r2, 1
or $r3, $r4, $r0
or $r4, $r5, $r0
add $r5, $r4, $r3
slt $r6, $r2, $r1
bne $r6, $r0, -5


