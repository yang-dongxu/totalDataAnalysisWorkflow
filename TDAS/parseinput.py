import sys
import os
import logging
from copy import deepcopy

from TDAS.combine_modules import Intermedia

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
        if not len(lineSplit):
            continue
        project=lineSplit[0]
        for i in range(0,len(names)):
            term=names[i]
            value=lineSplit[i].strip()
            Intermedia.add_term(part,project,term,str(value))
            cmd=f'echo "###### start process pipline ######"'
            cmd_part="1"
            Intermedia.add_term(part,project,term="command",value=cmd)
            Intermedia.add_term(part,project,term="command_part",value=cmd_part)
        if "seq_order"  not in names:
            Intermedia.add_term(part,project,term="seq_order",value="1")
        if "config_id" not in names:
            Intermedia.add_term(part,project,term="config_id",value=DEFAULT_CONFIG_ID)

    
    f.close()
    logging.info(Intermedia.get_str())
    return Intermedia

def parse_dirs(config:dict,dir:str):
    logging.info("you are using a testing function!")

