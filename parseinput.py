import sys
import os
import logging
from copy import deepcopy

from combine_modules import Intermedia

DEFAULT_CONFIG_ID="DEFAULT"

def parse_inputfile(config:dict,seqs:str):
    seqinfo_file=os.path.abspath(seqs)
    logging.info(f"input seq info file is  {seqinfo_file}")

    names=config["seq_info_format"][1:]
    sep=config["seq_info_format"][0]
    if sep=="":
        sep=None
    f=open(seqinfo_file,'r')
    part="raw"

    for line in f:
        lineSplit=line.split(sep)
        project=lineSplit[0]
        if len(lineSplit)<len(names) or lineSplit[-1]=="":
            lineSplit=lineSplit+[DEFAULT_CONFIG_ID]
        for i in range(0,len(names)):
            term=names[i]
            value=lineSplit[i]
            Intermedia.add_term(part,project,term,value)
            cmd=f'echo "###### start process pipline ######"'
            cmd_part="1"
            Intermedia.add_term(part,project,term="command",value=cmd)
            Intermedia.add_term(part,project,term="command_part",value=cmd_part)
    
    f.close()
    logging.info(Intermedia.get_str())
    return Intermedia

def parse_dirs(config:dict,dir:str):
    logging.info("you are using a testing function!")

