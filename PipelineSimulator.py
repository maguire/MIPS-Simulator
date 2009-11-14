import Instruction
import Simulator
class PipelineSimulator(Simulator):
    
    #self.pipeline is a list<PipelineInstr>
    #with the mapping of:
    #   0 = Fetch
    #   1 = Write Back
    #   2 = Read
    #   3 = Execute 
    #   4 = Data Access
    def __init__(self, instrCollection):
        self.pipeline = []
        Simulator.__init__(self, instrCollection)
    
    
    def step(self):
        #call advance on each instruction in the pipeline
        #TODO implement harzard control
        for pi in self.pipeline
            pi.advance()
        
        #shift the instructions to the next logical place
        #technically we do the Fetch instruction here, which is why 
        #FetchInstr.advance() does nothing
        self.pipeline[0] = FetchInstr(self.instrCollection[self.programCounter])
        self.pipeline[1] = WriteInstr(self.pipeline[4].instr)
        self.pipeline[2] = ReadInstr(self.pipeline[0].instr)
        self.pipeline[3] = ExecInstr(self.pipeline[2].instr)
        self.pipeline[4] = DataInstr(self.pipeline[3].instr)

        self.programCounter += 1
    def run(self):

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
        self.simulator.source1RegValue = self.simulator.registers[self.instruction.sourceRegister1]
        self.simulator.source2RegValue = self.simulator.registers[self.instruction.sourceRegister2]

class ExecInstr(PipelineInstr):
    

    def advance(self):
        """
        Execute the instruction according to its mapping of 
        assembly operation to python operation
        """
        self.simulator.result = eval("%d %s %d" % (self.simulator.source1RegValue,Simulator.operations[self.instruction.name],self.simulator.source2RegValue))

class DataInstr(PipelineInstr):
   def advance(self):
        """
        If we have to write to main memory, write it first
        and then read from main memory second
        """
 
        if self.instruction.writeMem :
            self.simulator.mainmemory[int(self.instruction.memoryAddress)] = self.simulator.source1RegValue
        else if self.instruction.readMem :
            self.simulator.source1RegValue = self.simulator.main[int(self.instruction.memoryAddress)]
class WriteInstr(PipelineInstr):
    def advance(self):
        """
        Write to the register file
        """
        if self.instruction.regWrite:
            self.simulator.registers[self.instruction.destinationReg] = self.simulator.result
