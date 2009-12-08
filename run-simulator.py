import PipelineSimulator
import Instruction
import os
import sys

def main():
    iparser = Instruction.InstructionParser()
    pipelinesim = PipelineSimulator.PipelineSimulator(iparser.parseFile(sys.argv[1]))
    pipelinesim.run()

if __name__ == "__main__":
    main()

