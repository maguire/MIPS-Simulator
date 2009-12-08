ori $r1, $r0, 100
ori $r2, $r0, 5
ori $r3, $r0, 7
sw $r2, 0($r1)
sw $r3, 4($r1)
add $r2, $r1, $r1
add $r3, $r1, $r1
lw $r2, 0($r1)
lw $r3, 4($r1)
add $r5, $r2, $r3
