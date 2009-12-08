from Instruction import *
import collections 

class PipelineSimulator(object): 
    operations = {'add' : '+', 'addi' : '+', 'sub' : '-', 'subi' : '-', 
                  'and' : '&', 'andi' : '&', 'or'  : '|', 'ori'  : '|'} 
                  
    def __init__(self,instrCollection):
        self.hazardList = []
        self.source1RegValue = [] 
        self.source2RegValue = []
        self.__done = False
        self.branched = False
        self.jumped = False
        self.stall = False
        
        #self.pipeline is a list<PipelineStage>
        #with the mapping of:
        #   0 = Fetch
        #   1 = Write Back
        #   2 = Read
        #   3 = Execute 
        #   4 = Data Access
        self.pipeline = [None for x in range(0,5)]

        self.pipeline[0] = FetchStage(Nop, self)
        self.pipeline[1] = WriteStage(Nop, self)
        self.pipeline[2] = ReadStage(Nop, self)
        self.pipeline[3] = ExecStage(Nop, self)
        self.pipeline[4] = DataStage(Nop, self)
        
        # ex: {'$r0' : 0, '$r1' : 0 ... '$r31' : 0 }
        self.registers = dict([("$r%s" % x, 0) for x in range(32)]) 
        
        # set up the main memory construct, a list index starting at 0
        # and continuing to 0xffc
        self.mainmemory = [0 for x in range(0xffc/4)]

        # programCounter to state where in the instruction collection
        # we are. to find correct spot in mainmemory add 0x100  
        self.programCounter = 0

        # the list of instruction objects passed into the simulator,
        # most likely created by parsing text 
        self.instrCollection = instrCollection
       
        # populate main memory with our text of the instructions
        # starting at 0x100
        y = 0
        for x in range(0x100/4, len(self.mainmemory)):
            if y < len(self.instrCollection):
                self.mainmemory[x] = self.instrCollection[y]
                y += 1
            else: 
                break

    def step(self):
        #shift the instructions to the next logical place
        #technically we do the Fetch instruction here, which is why 
        #FetchStage.advance() does nothing
        
        #MUST KEEP THIS ORDER
        self.pipeline[1] = WriteStage(self.pipeline[4].instr,self)
        if self.stall :
            self.pipeline[4] = DataStage(Nop,self)
        else :
            self.pipeline[4] = DataStage(self.pipeline[3].instr,self)
            self.pipeline[3] = ExecStage(self.pipeline[2].instr,self)
            self.pipeline[2] = ReadStage(self.pipeline[0].instr,self)
            self.pipeline[0] = FetchStage(None, self)
         
        #call advance on each instruction in the pipeline
        #TODO implement hazard control
        for pi in self.pipeline:
                pi.advance()
       
        if (self.pipeline[1].instr.regWrite) :
            self.hazardList.pop(0)

        self.checkDone()

        #TODO do not always update program counter, actually we should find a good way
        # to exit the program
        if not (self.stall or self.branched or self.jumped):
            self.programCounter += 1
        else:
            self.stall = False
            self.branched = False
            self.jumped = False
    
    def checkDone(self):
        self.__done = True
        for pi in self.pipeline:
            if pi.instr is not Nop:
                self.__done = False
    
    def run(self):
        while not self.__done:
            self.step()
            self.debug()
    
    def getForwardVal(self, regName):
        if (self.pipeline[4] is not Nop 
                and self.pipeline[4].instr.result is not None
                and self.pipeline[4].instr.dest == regName) :
                    return self.pipeline[4].instr.result
        elif (self.pipeline[1] is not Nop
                and self.pipeline[1].instr.dest == regName ):
                    return self.pipeline[1].instr.result
        else :
            return False
    
    def debug(self):
        print "######################## debug ###########################"
        self.printStageCollection() 
        self.printRegFile()
        print "\n<ProgramCounter>", self.programCounter
        #print("MainMemory: ", self.mainmemory)
        self.printPipeline()   
        #print "Result", self.result
         
    def printPipeline(self):
        print "\n<Pipeline>"
        print repr(self.pipeline[0]) 
        print repr(self.pipeline[2]) 
        print repr(self.pipeline[3]) 
        print repr(self.pipeline[4]) 
        print repr(self.pipeline[1]) 

    def printRegFile(self):
        #"""
        print "\n<Register File>"
        for k,v in sorted(self.registers.iteritems()):
            if len(k) != 3:
                print k, " : " , v,
            else :
                print "\n",k, " : ", v,
        """
        print "\n<Register File>"
        count = 0
        for k,v in sorted(self.registers.iteritems()):
            if count < 8:
                print "{0}:{1}".format(k,v), 
            else:
                print "\n{0}:{1}".format(k,v), 
                count = 0
        """ 
                
    def printStageCollection(self):
        """
        print "Instruction Collection:" 
        y = 1
        for v in self.instrCollection : 
            print y, " : " ,str(v)
            y+=1
        """
        print "<Instruction Collection>"
        for index, item in enumerate(self.instrCollection):
            print index, ": ", str(item)

class PipelineStage(object):
    def __init__(self, instruction, simulator):
        self.instr = instruction
        self.simulator = simulator
        
    def advance(self):
        pass
    
    def __repr__(self):
        return str(self) + ':\t' + str(self.instr)
    
class FetchStage(PipelineStage):
    def advance(self):
        """ 
        Fetch the next instruction according to simulator program counter
        """
        if self.simulator.programCounter < len(self.simulator.instrCollection):
            self.instr = self.simulator.instrCollection[self.simulator.programCounter]
        else:    
            self.instr = Nop
    
    def __str__(self):
        return 'Fetch Stage\t'
    
class ReadStage(PipelineStage):
    def advance(self):
        """
        Read the necessary registers from the registers file
        used in this instruction 
        """
        
        if(self.instr.regRead):
            self.simulator.source1RegValue.append(self.simulator.registers[self.instr.s1])
            if self.instr.immed:
                self.simulator.source2RegValue.append(int(self.instr.immed))
            elif self.instr.s2:
                self.simulator.source2RegValue.append(self.simulator.registers[self.instr.s2])
                
        if self.instr.op == 'j':
            # Set the program counter to the raw target address
            self.simulator.programCounter = self.instr.target
            # Set the other instructions currently in the pipeline to a Nop
            self.simulator.pipeline[0] = FetchStage(Nop, self)
            self.simulator.jumped = True
        elif self.instr.op == 'jr':
            self.simulator.programCounter = self.simulator.registers[self.instr.target]
            # Set the other instructions currently in the pipeline to a Nop
            self.simulator.pipeline[0] = FetchStage(Nop, self)
            self.simulator.jumped = True
    def __str__(self):
        return 'Read from Register'
    
class ExecStage(PipelineStage):
    def advance(self):
        """
        Execute the instruction according to its mapping of 
        assembly operation to Python operation
        """
         
        if self.instr is not Nop and self.instr.aluop:
            if self.instr.s1 in self.simulator.hazardList :
                forwardVal = self.simulator.getForwardVal(self.instr.s1)
                print "s1 forward" ,forwardVal
                if forwardVal :
                    self.simulator.source1RegValue[0] = forwardVal
                else :
                    self.simulator.stall = True
                    return
            if self.instr.s2 in self.simulator.hazardList :
                forwardVal = self.simulator.getForwardVal(self.instr.s2)
                print "s2 forward" , forwardVal 
                if forwardVal :
                    self.simulator.source2RegValue[0] = forwardVal
                else :
                    self.simulator.stall = True
                    return
            
                
            self.simulator.hazardList.append(self.instr.dest)    
            #TODO add special cases instead of just an eval (branch jump)
            if self.instr.op == 'bne':
                if self.instr.dest != self.instr.s1:
                    # Set the program counter to the target address
                    self.simulator.programCounter = self.simulator.programCounter + int(self.instr.immed)
                    # Set the other instructions currently in the pipeline to Nops
                    self.simulator.pipeline[0] = FetchStage(Nop, self)
                    self.simulator.pipeline[2] = ReadStage(Nop, self)
                    self.simulator.branched = True
            elif self.instr.op == 'beq':
                if self.instr.dest == self.instr.s1:
                    # Set the program counter to the target address
                    self.simulator.programCounter = self.simulator.programCounter + int(self.instr.immed)
                    # Set the other instructions currently in the pipeline to Nops
                    self.simulator.pipeline[0] = FetchStage(Nop, self)
                    self.simulator.pipeline[2] = ReadStage(Nop, self)
                    self.simulator.branched = True
            else :         
                if (self.instr.op == 'slt'):
                    val = 1 if self.simulator.source1RegValue.pop(0) < self.simulator.source2RegValue.pop(0) else 0
                    self.instr.result = val
                elif (self.instr.op == 'nor'):
                    self.instr.result = ~(self.simulator.source1RegValue.pop(0) | self.simulator.source2RegValue.pop(0))
                else:
                    self.instr.result = eval("%d %s %d" % 
                                                        (self.simulator.source1RegValue.pop(0),
                                                        self.simulator.operations[self.instr.op],
                                                        self.simulator.source2RegValue.pop(0)))
                
        #print self.simulator.source1RegValue , " " , self.simulator.source2RegValue
        
    def __str__(self):
        return 'Execute Stage\t'
    
class DataStage(PipelineStage):
    def advance(self):
        """
        If we have to write to main memory, write it first
        and then read from main memory second
        """
 
        if self.instr.writeMem:
            self.simulator.mainmemory[self.instr.s2] = self.simulator.source1RegValue
        else:
            if self.instr.readMem:
                self.instr.result = self.simulator.mainmemory[self.instr.s2]
    def __str__(self):
        return 'Main Memory\t'
    
class WriteStage(PipelineStage):
    def advance(self):
        """
        Write to the register file
        """
        if self.instr.regWrite:
            if self.instr.dest == '$r0':
                #Edit: don't raise exception just ignore it
                #raise Exception('Cannot assign to register $r0')    
                pass
            elif self.instr.dest:
                self.simulator.registers[self.instr.dest] = self.instr.result
                
    def __str__(self):
        return 'Write to Register'
