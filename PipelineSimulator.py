from Instruction import *
import collections 

class PipelineSimulator(object): 
    operations = {'add' : '+', 'addi' : '+', 'sub' : '-', 'subi' : '-', 
                  'and' : '&', 'andi' : '&', 'or'  : '|', 'ori'  : '|'} 
                  
    def __init__(self,instrCollection):
        self.instrCount = 0
        self.cycles = 0
        self.hazardList = []
        self.__done = False
        self.branched = False
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
        self.mainmemory = dict([(x*4, 0) for x in range(0xffc/4)])

        # programCounter to state where in the instruction collection
        # we are. to find correct spot in mainmemory add 0x100  
        self.programCounter = 0x1000

        # the list of instruction objects passed into the simulator,
        # most likely created by parsing text 
        self.instrCollection = instrCollection
       
        # populate main memory with our text of the instructions
        # starting at 0x100
        y=0
        for instr in self.instrCollection:
           self.mainmemory[0x1000 + y] = instr
           y += 4
    
    def step(self):
        self.cycles +=1
        #shift the instructions to the next logical place
        #technically we do the Fetch instruction here, which is why 
        #FetchStage.advance() does nothing
        
        #MUST KEEP THIS ORDER
        self.pipeline[1] = WriteStage(self.pipeline[4].instr,self)
        if self.stall :
            self.pipeline[4] = DataStage(Nop,self)
            self.stall = False
        else :
            self.pipeline[4] = DataStage(self.pipeline[3].instr,self)
            self.pipeline[3] = ExecStage(self.pipeline[2].instr,self)
            self.pipeline[2] = ReadStage(self.pipeline[0].instr,self)
            self.pipeline[0] = FetchStage(None, self)
         
        #call advance on each instruction in the pipeline
        for pi in self.pipeline:
                pi.advance()
        #now that everything is done, remove the register from
        # the hazard list
        if (self.pipeline[1].instr.regWrite) :
            self.hazardList.pop(0)
        
        self.checkDone()

        #if we stalled our branched we didn't want to load a new
        # so keep the program counter where it is
        if self.stall or self.branched:
            self.programCounter -= 4 
            self.branched = False
    
    def checkDone(self):
        """ Check if we are done and set __done variable """
        self.__done = True
        for pi in self.pipeline:
            if pi.instr is not Nop:
                self.__done = False
    
    def run(self):
        """ Run the simulator, call step until we are done """
        while not self.__done:
            self.step()
            self.debug()
    
    def getForwardVal(self, regName):
        """ Forward the proper value based on the given register name
            If the value is not ready, return "GAH" 
        """
        if (self.pipeline[4] is not Nop 
                and self.pipeline[4].instr.result is not None
                and self.pipeline[4].instr.dest == regName) :
                    return self.pipeline[4].instr.result
        elif (self.pipeline[1] is not Nop
                and self.pipeline[1].instr.dest == regName ):
                    return self.pipeline[1].instr.result
        else :#this value used to be False, but python treats False and 0 the same
            return "GAH" 

    ### DEBUGGING INFORMATION PRINTING ### 
    def debug(self):
        print "######################## debug ###########################"
        self.printStageCollection() 
        self.printRegFile()
        print "\n<ProgramCounter>", self.programCounter
        self.printPipeline()   
        print "<CPI> : " , float(self.cycles) / float(self.instrCount) 
        print "<Hazard List> : " , self.hazardList

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
                
    def printStageCollection(self):
        print "<Instruction Collection>"
        for index, item in sorted(self.mainmemory.iteritems()):
            if item != 0:
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
        if self.simulator.programCounter < (len(self.simulator.instrCollection) * 4 + 0x1000):
            self.simulator.instrCount += 1
            self.instr = self.simulator.mainmemory[self.simulator.programCounter]
        else:
            self.instr = Nop
        self.simulator.programCounter += 4
         
    def __str__(self):
        return 'Fetch Stage\t'
    
class ReadStage(PipelineStage):
    def advance(self):
        """
        Read the necessary registers from the registers file
        used in this instruction 
        """
        
        if(self.instr.regRead):
            self.instr.source1RegValue = self.simulator.registers[self.instr.s1]
            if (self.instr.immed and
                #these instructions require special treatment
                 not( self.instr.op == 'bne' or self.instr.op == 'beq' 
                     or self.instr.op =='lw' or self.instr.op =='sw')): 
                #check to see if it is a hex value
                if "0x" in self.instr.immed:
                    self.instr.source2RegValue = int(self.instr.immed,16)
                else :
                    self.instr.source2RegValue = int(self.instr.immed)
            elif self.instr.s2:
                self.instr.source2RegValue = self.simulator.registers[self.instr.s2]
                    
        if self.instr.op == 'j':
            # Set the program counter to the raw target address
            if "0x" in self.instr.target:
                    targetval = int(self.instr.target, 16)
            else :
                    targetval = int(self.instr.target)
            self.simulator.programCounter = targetval
            # Set the other instructions currently in the pipeline to a Nop
            self.simulator.pipeline[0] = FetchStage(Nop, self)
    def __str__(self):
        return 'Read from Register'
    
class ExecStage(PipelineStage):
    def advance(self):
        """
        Execute the instruction according to its mapping of 
        assembly operation to Python operation
        """
        
        
        if self.instr is not Nop and self.instr.aluop:
            #if we have a hazard in either s1 or s2, 
            # grab the value from the other instructions
            # in the pipeline
            if self.instr.s1 in self.simulator.hazardList :
                forwardVal = self.simulator.getForwardVal(self.instr.s1)
                if forwardVal != "GAH":
                    self.instr.source1RegValue = forwardVal
                else :
                    self.simulator.stall = True
                    return
            if self.instr.s2 in self.simulator.hazardList :
                forwardVal = self.simulator.getForwardVal(self.instr.s2)
                if forwardVal != "GAH" :
                    self.instr.source2RegValue = forwardVal
                else :
                    self.simulator.stall = True
                    return
            
            #append the destination register to the hazard list 
            if self.instr.regWrite :
                self.simulator.hazardList.append(self.instr.dest)    

            #calculate the offset of the lw and sw instructions
            if  self.instr.op == 'lw':
                self.instr.source1RegValue = self.instr.source1RegValue + int(self.instr.immed)
            elif  self.instr.op == 'sw':
                self.instr.source2RegValue = self.instr.source2RegValue + int(self.instr.immed)
            elif self.instr.op == 'jr':
                self.simulator.programCounter = self.instr.source1RegValue
                # Set the other instructions currently in the pipeline to a Nop
                self.simulator.pipeline[0] = FetchStage(Nop, self)
                self.simulator.pipeline[2] = ReadStage(Nop, self)
            elif self.instr.op == 'bne':
                if self.instr.source1RegValue != self.instr.source2RegValue:
                    # Set the program counter to the target address 
                    # subtract 8 to account for 2 instructions we have loaded into fetch and read
                    self.simulator.programCounter = self.simulator.programCounter + (int(self.instr.immed) * 4) - 8
                    # Set the other instructions currently in the pipeline to Nops
                    self.simulator.pipeline[0] = FetchStage(Nop, self)
                    self.simulator.pipeline[2] = ReadStage(Nop, self)
                    self.simulator.branched = True
            elif self.instr.op == 'beq':
                if self.instr.source1RegValue == self.instr.source2RegValue:
                    # Set the program counter to the target address
                    self.simulator.programCounter = self.simulator.programCounter + (int(self.instr.immed) * 4) - 8
                    # Set the other instructions currently in the pipeline to Nops
                    self.simulator.pipeline[0] = FetchStage(Nop, self)
                    self.simulator.pipeline[2] = ReadStage(Nop, self)
                    self.simulator.branched = True
            else :         
                if (self.instr.op == 'slt'):
                    val = 1 if self.instr.source1RegValue < self.instr.source2RegValue else 0
                    self.instr.result = val
                elif (self.instr.op == 'nor'):
                    self.instr.result = ~(self.instr.source1RegValue | self.instr.source2RegValue)
                else:
                    self.instr.result = eval("%d %s %d" % 
                                                        (self.instr.source1RegValue,
                                                        self.simulator.operations[self.instr.op],
                                                        self.instr.source2RegValue))
                
    def __str__(self):
        return 'Execute Stage\t'
    
class DataStage(PipelineStage):
    def advance(self):
        """
        If we have to write to main memory, write it first
        and then read from main memory second
        """
 
        if self.instr.writeMem:
            self.simulator.mainmemory[self.instr.source2RegValue] = self.instr.source1RegValue
        elif self.instr.readMem:
            self.instr.result = self.simulator.mainmemory[self.instr.source1RegValue]
    def __str__(self):
        return 'Main Memory'
    
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
