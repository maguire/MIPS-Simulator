'''
Created on Dec 7, 2009

@author: greg
'''

from Instruction import *
from PipelineSimulator import *

if __name__ == '__main__':
    parser = InstructionParser()
    collection = parser.parseFile('loop.s')
    mips = PipelineSimulator(collection)
    
    mips.run()


