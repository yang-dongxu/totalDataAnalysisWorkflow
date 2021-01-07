from Intermedia import Intermedia
import sys
import os

from pandas.io.json._normalize import nested_to_record 

from functions import *


METHOD={
    "trim":trim,
    "STAR":star,
    "featureCounts":featureCounts,
    "format":format,
    "redistribute":redistribute,

} 
     
def out_bash_cmd(cmds):
    for name,cmd in cmds.items():
        mkdirs(os.path.split(name)[0])
        with open(name,'w') as f:
            f.write("\n".join(cmd))
    return True

def process(config:dict,root_out_dir=""):
    for i in Intermedia.get_next_to_process():
        raw,project,configid=i
        this_config=config[configid]
        if len(root_out_dir)==0:
            outdir=os.path.join(os.getcwd(),this_config["outdir"])
        else:
            outdir=os.path.abspath(root_out_dir)
        mkdirs(outdir)
        for part in this_config["order"]:
            partname=part.strip().split("/")[0]
            func=METHOD[partname]
            func_config=this_config["workflow"][part]
            func(func_config,outdir,project,part)
    if len(root_out_dir)==0:
        outdir=""
    else:
        outdir=os.path.abspath(root_out_dir)
    out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir))