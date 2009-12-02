"""
Instructions to support:

R-Type Instructions [add, sub, and, or, jr, nor, slt]
opcode(6), rs(5), rt(5), rd(5), sa(5), func(6)
I-Type Instructions [addi, subi, ori, bne, beq, lw, sw]
opcode(6), rs(5), rt(5), immediate(16)
J-Type Instructions [j]
opcode(6), target(26)

instr - type of instruction
op - operation
rs - source register
rt - transition register
rd - destination register
sa (shamt) - shift amount
target - target address
func - function
"""

class Instruction(object):
    def __init__(self, **input):
        self.values = {
                       'op': None,
                       'rs': None,
                       'rt': None,
                       'rd': None,
                       'immed': None,
                       'target': None
        }
        self.controls = {'regRead' : None,
                         'regWrite': None,
                         'readMem' : None,
                         'writeMem': None, }

        for key in input:
            if key in self.values.keys():
                self.values[key] = input[key]
            else :
                self.controls[key] = input[key]
    
    def __str__(self):
        return repr(self.values)
        
class InstructionParser(object):
    def __init__(self):
        self.instructionSet = {
            'rtype': ['add', 'sub', 'and', 'or', 'jr', 'nor', 'slt'],
            'itype': ['addi', 'subi', 'ori', 'bne', 'beq', 'lw', 'sw'],
            'jtype': ['j']
        }    

    def parseFile(self, filename):
        with open(filename) as f:
            data = f.readlines()
            instructions = [self.parse(a.replace(',',' ')) for a in data]
            return instructions

    def parse(self, s):
        s = s.split()
        
        instr = s[0]
        
        if instr in self.instructionSet['rtype']:
            return self.createRTypeInstruction(s)
        elif instr in self.instructionSet['itype']:
            return self.createITypeInstruction(s)    
        elif instr in self.instructionSet['jtype']:
            return self.createJTypeInstruction(s)
        else:
            raise ParseError("Invalid parse instruction")

    def createRTypeInstruction(self, s):
        return Instruction(op=s[0], rd=s[1], rs=s[2], rt=s[3], regRead = 1, regWrite =1)

    def createITypeInstruction(self, s):
        return Instruction(op=s[0], rs=s[1], rt=s[2], immed=s[3], regRead=1, regWrite=1)

    def createJTypeInstruction(self, s):
        return Instruction(op=s[0], target=s[1])

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
