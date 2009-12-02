import PipelineSimulator
import Instruction
import os
import sys

def main():
    iparser = Instruction.InstructionParser()
    pipelinesim = PipelineSimulator.PipelineSimulator(iparser.parseFile(sys.argv[1]))
    pipelinesim.step()
    pipelinesim.debug()

    pipelinesim.step()
    pipelinesim.debug()
    pipelinesim.step()
    pipelinesim.debug()
    pipelinesim.step()
    pipelinesim.debug()
    pipelinesim.step()
    pipelinesim.debug()

    pipelinesim.step()
    pipelinesim.debug()
if __name__ == "__main__":
    main()

