import Instruction
import collections 
class PipelineSimulator(object):
     
    operations = {'add' : '+', 'addi' : '+', 'sub' : '-', 'subi' : '-', 
                  'and' : '&', 'andi' : '&', 'or'  : '|', 'ori'  : '|'} 
                  
    def __init__(self,instrCollection):
        self.result = []
        self.source1RegValue = [] 
        self.source2RegValue = []
        self._done = False
        
        #self.pipeline is a list<PipelineInstr>
        #with the mapping of:
        #   0 = Fetch
        #   1 = Write Back
        #   2 = Read
        #   3 = Execute 
        #   4 = Data Access
        self.pipeline = [None for x in range(0,5)]

        self.pipeline[0] = FetchInstr(Instruction.Nop, self)
        self.pipeline[1] = WriteInstr(Instruction.Nop, self)
        self.pipeline[2] = ReadInstr(Instruction.Nop, self)
        self.pipeline[3] = ExecInstr(Instruction.Nop, self)
        self.pipeline[4] = DataInstr(Instruction.Nop, self)
        
        # ex: {'$r0' : 0, '$r1' : 0 ... '$r31' : 0 }
        self.registers = dict([("$r%s" % x, 0) for x in range(32)]) 
        
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
                self.mainmemory[x] = self.instrCollection[y]
                y += 1
            else: 
                break

    def step(self):
        #shift the instructions to the next logical place
        #technically we do the Fetch instruction here, which is why 
        #FetchInstr.advance() does nothing
        
        #MUST KEEP THIS ORDER
        self.pipeline[1] = WriteInstr(self.pipeline[4].instr,self)
        self.pipeline[4] = DataInstr(self.pipeline[3].instr,self)
        self.pipeline[3] = ExecInstr(self.pipeline[2].instr,self)
        self.pipeline[2] = ReadInstr(self.pipeline[0].instr,self)
        
        if self.programCounter < len(self.instrCollection) :
            self.pipeline[0] = FetchInstr(self.instrCollection[self.programCounter],self)
        else:    
            self.pipeline[0] = FetchInstr(Instruction.Nop, self)
        #call advance on each instruction in the pipeline
        #TODO implement harzard control
        for pi in self.pipeline:
                pi.advance()
        

       
        self.checkDone()

        #TODO do not always update program counter, actually we should find a good way
        # to exit the program
        self.programCounter += 1
    
    def checkDone(self):
        self._done = True
        for pi in self.pipeline:
            if pi.instr is not Instruction.Nop:
                self._done = False
    
    def run(self):
        while not self._done :
            self.step()
            self.debug()
    
    def debug(self):
        print "######################## debug ###########################"
        self.printInstrCollection() 
        self.printRegFile()
        print "\n\nProgramCounter: ", self.programCounter
        #print("MainMemory: ", self.mainmemory)
        self.printPipeline()   
        print "Result" , self.result 
    def printPipeline(self):
        print "\nPipeline : "
        print repr(self.pipeline[0]) 
        print repr(self.pipeline[2]) 
        print repr(self.pipeline[3]) 
        print repr(self.pipeline[4]) 
        print repr(self.pipeline[1]) 

    def printRegFile(self):
        print "\nRegister File:"
        for k,v in sorted(self.registers.iteritems()):
            if len(k) != 3:
                print k, " : " , v,
            else :
                print "\n",k, " : ", v,
    def printInstrCollection(self):
        print "Instruction Collection:" 
        y = 1
        for v in self.instrCollection : 
            print y, " : " ,str(v)
            y+=1

class PipelineInstr(object):
    
    def __init__(self, instruction, simulator):
        self.instr = instruction
        self.simulator = simulator
    def advance(self):
        pass
    def __repr__(self):
        return str(self) + ':\t' + str(self.instr)
class FetchInstr(PipelineInstr):
    
    def advance(self):
        """ 
        Pretty Much does nothing in our simulator.
        """
        pass
    def __str__(self):
        return 'Fetch'
class ReadInstr(PipelineInstr):
    
    def advance(self):
        """
        Read the necessary registers from the registers file
        used in this instruction 
        """
        
        if(self.instr.controls['regRead']):
            self.simulator.source1RegValue.append(self.simulator.registers[self.instr.values['s1']])
            if self.instr.values['immed'] is not None:
                self.simulator.source2RegValue.append(int(self.instr.values['immed']))
            elif self.instr.values['s2'] is not None:
                self.simulator.source2RegValue.append(self.simulator.registers[self.instr.values['s2']])
    def __str__(self):
        return 'Read'
class ExecInstr(PipelineInstr):
    
    def advance(self):
        """
        Execute the instruction according to its mapping of 
        assembly operation to python operation
        """
        #TODO add special cases instead of just an eval (branch jump)
        if self.instr is not Instruction.Nop and self.instr.controls['aluop']:
            if (self.instr.values['op'] == 'slt') :
                self.simulator.result.append(1 if self.simulator.source1RegValue.pop(0) < self.simulator.source2RegValue.pop(0) else 0)
            elif (self.instr.values['op'] == 'nor') :
                self.simulator.result.append( ~(self.simulator.source1RegValue.pop(0) | self.simulator.source2RegValue.pop(0)))
            else :
                self.simulator.result.append(eval("%d %s %d" % 
                                                    (self.simulator.source1RegValue.pop(0),
                                                    PipelineSimulator.operations[self.instr.values['op']],
                                                    self.simulator.source2RegValue.pop(0))))
        print self.simulator.source1RegValue , " " , self.simulator.source2RegValue
    def __str__(self):
        return 'Exec'
class DataInstr(PipelineInstr):
   def advance(self):
        """
        If we have to write to main memory, write it first
        and then read from main memory second
        """
 
        if self.instr.controls['writeMem'] :
            self.simulator.mainmemory[int(self.instr.values['s2'])] = self.simulator.source1RegValue
        else:
            if self.instr.controls['readMem'] :
                self.simulator.source1RegValue = self.simulator.main[int(self.instr.values['s2'])]
   def __str__(self):
        return 'Memory'
class WriteInstr(PipelineInstr):
    def advance(self):
        """
        Write to the register file
        """
        if self.instr.controls['regWrite'] :
            if self.instr.values['dest'] == '$r0':
                raise Exception('Cannot assign to register $r0')    
            else:
                self.simulator.registers[self.instr.values['dest']] = self.simulator.result.pop(0)
    def __str__(self):
        return 'Write'
