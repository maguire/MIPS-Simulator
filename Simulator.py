
import Instruction 
import os


instrCollection = parseFile(sys.argv[1])
class Simulator(object):

    operations = {'add' : '+', 'addi' : '+', 'sub' : '-', 'subi' : '-', 
                  'and' : '&', 'andi' : '&', 'or'  : '|', 'ori'  : '|', 
                  'nor' : '~|', 'slt' : '<'}
    def __init__(self, instrCollection):
        # set up the registers file, a dictionary mapping.
        # ex: {'r0' : 0, 'r1' : 0 ... 'r31' : 0 }
        self.registers = dict([("r%s" % x, 0) for x in range(32)]) 
        
        #set up the main memory construct, a list index starting at 0
        # and continuing to 0xffc
        self.mainmemory = [0 for x in range(int(0xffc))]

        # programCounter to state where in the instruction collection
        # we are. to find correct spot in mainmemory add 0x100  
        self.programCounter = 0

        # the list of instruction objects passed into the simulator,
        # most likely created by parsing text 
        self.instrCollection = instrCollection
        
        # populate main memory with our text of the instructions
        # starting at 0x100
        y = 0
        for x in range(int(0x100), len(mainmemory)):
            if(y < len(instrCollection):
                mainmemory[x] = instrCollection[y].text
                y += 1
            else: 
                break
    #the following would be defined by single cycle simulator
    # if we were implementing one
    def run(self):
        pass 
    def step(self):
        pass


