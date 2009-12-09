#!/usr/bin/python

import PipelineSimulator
import Instruction
import os
import sys

def main():
    iparser = Instruction.InstructionParser()
    pipelinesim = PipelineSimulator.PipelineSimulator(iparser.parseFile(sys.argv[1]))
    
    filename = sys.argv[2] if len(sys.argv) > 2 else "debug.txt"
    f = open(filename, 'w')
    sys.stdout = f
    pipelinesim.run()

if __name__ == "__main__":
    main()

