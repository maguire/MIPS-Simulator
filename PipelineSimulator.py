import Instruction
import os

class PipelineSimulator(object):
     
    operations = {'add' : '+', 'addi' : '+', 'sub' : '-', 'subi' : '-', 
                  'and' : '&', 'andi' : '&', 'or'  : '|', 'ori'  : '|', 
                  'nor' : '~|', 'slt' : '<'}
    def __init__(self,instrCollection):
        #self.pipeline is a list<PipelineInstr>
        #with the mapping of:
        #   0 = Fetch
        #   1 = Write Back
        #   2 = Read
        #   3 = Execute 
        #   4 = Data Access
        self.pipeline = []
        # ex: {'r0' : 0, 'r1' : 0 ... 'r31' : 0 }
        self.registers = dict([("r%s" % x, 0) for x in range(32)]) 
        
        #set up the main memory construct, a list index starting at 0
        # and continuing to 0xffc
        self.mainmemory = [0 for x in range(int(0xffc)/4)]

        # programCounter to state where in the instruction collection
        # we are. to find correct spot in mainmemory add 0x100  
        self.programCounter = 0

        # the list of instruction objects passed into the simulator,
        # most likely created by parsing text 
        self.instrCollection = instrCollection
        
        # populate main memory with our text of the instructions
        # starting at 0x100
        y = 0
        for x in range(int(0x100)/4, len(self.mainmemory)):
            if y < len(self.instrCollection):
                self.mainmemory[x] = self.instrCollection[y].text
                y += 1
            else: 
                break
    
    def step(self):
        #call advance on each instruction in the pipeline
        #TODO implement harzard control
        for pi in self.pipeline:
            pi.advance()
        
        #shift the instructions to the next logical place
        #technically we do the Fetch instruction here, which is why 
        #FetchInstr.advance() does nothing
        self.pipeline[0] = FetchInstr(self.instrCollection[self.programCounter],self)
        self.pipeline[1] = WriteInstr(self.pipeline[4].instr,self)
        self.pipeline[2] = ReadInstr(self.pipeline[0].instr,self)
        self.pipeline[3] = ExecInstr(self.pipeline[2].instr,self)
        self.pipeline[4] = DataInstr(self.pipeline[3].instr,self)

        self.programCounter += 1
    def run(self):
        pass

class PipelineInstr(object):
    
    def __init__(self, instruction, simulator):
        self.instr = instruction
        self.simulator = simulator
    
    def advance(self):
        pass

class FetchInstr(PipelineInstr):
    
    def advance(self):
        """ 
        Pretty Much does nothing in our simulator.
        """
        pass
class ReadInstr(PipelineInstr):
    
    def advance(self):
        """
        Read the necessary registers from the registers file
        used in this instruction 
        """
        if(self.instruction.regRead):
            self.simulator.source1RegValue = self.simulator.registers[self.instruction.values.rt]
        if self.instruction.values.rd is None
            self.simulator.source2RegValue = 
                    self.simulator.registers[self.instruction.values.rd]

class ExecInstr(PipelineInstr):
    
    def advance(self):
        """
        Execute the instruction according to its mapping of 
        assembly operation to python operation
        """
        #TODO add special cases instead of just an eval 
        self.simulator.result = eval("%d %s %d" % 
                                        (self.simulator.source1RegValue,
                                         PipelineSimulator.operations[self.instruction.vales.op],
                                         self.simulator.source2RegValue))

class DataInstr(PipelineInstr):
   def advance(self):
        """
        If we have to write to main memory, write it first
        and then read from main memory second
        """
 
        if self.instruction.writeMem :
            self.simulator.mainmemory[int(self.instruction.values.rt)] = self.simulator.source1RegValue
        else:
            if self.instruction.readMem :
                self.simulator.source1RegValue = self.simulator.main[int(self.instruction.values.rs)]
class WriteInstr(PipelineInstr):
    def advance(self):
        """
        Write to the register file
        """
        if self.instruction.regWrite :
            self.simulator.registers[self.instruction.rs] = self.simulator.result
