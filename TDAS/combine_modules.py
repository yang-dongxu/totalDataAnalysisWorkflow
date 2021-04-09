import sys
import os

from pandas.io.json._normalize import nested_to_record 
import yaml

from TDAS.Intermedia import Intermedia
#from TDAS.functions import *
from TDAS.stats_functions import BlockStat
from TDAS.working_functions import BlockWork
from TDAS.spfunctions import SPfucntions,mkdirs

# METHOD={
#     "trim":trim,
#     "STAR":star,
#     "featureCounts":featureCounts,
#     "format":format,
#     "redistribute":redistribute,
#     "other":self_func

# } 

def determine_bg(cmd):
    if "&" not in cmd:
        return 0
    if "&&" not in  cmd:
        return 1
    
    last_cmd=cmd.split("&&")[-1]
    return determine_bg(last_cmd)
     
def out_bash_cmd(cmds,threads=2):
    for name in cmds:
        if os.path.exists(name):
                os.remove(name)
    count=0
    for name,cmd in cmds.items():
        mkdirs(os.path.split(name)[0])
        with open(name,'a+') as f:
            for i in cmd:
                f.write(i+"\n")
                count+=determine_bg(i)
                if count>=threads:
                    f.write("wait\n")
                    count=0


    return True

def out_intermedia(name):
    with open (name,'w') as f:
        f.write(Intermedia.dumps())
    return True  

def out_intermedia_new(config):
    for i in Intermedia.get_next_to_process(config):
        project,configid=i
        name=os.path.join(config[configid]["outdir"],config[configid]["data_name"])
        out_intermedia(name)
    return True  


def process(config:dict,root_out_dir="",stat=True,threads=8):
    for i in Intermedia.get_next_to_process(config):
        project,configid=i
        this_config=config[configid]
        if len(root_out_dir)==0:
            outdir=os.path.join(os.getcwd(),this_config["outdir"])
        else:
            outdir=os.path.abspath(root_out_dir)
        mkdirs(outdir)
        for part in this_config["order"]:
            partname=part.strip().split("/")[0]
            if partname in SPfucntions:
                func=SPfucntions[partname]
            else:
                func=SPfucntions["other"]
            func_config=this_config["workflow"][part]
            #func(func_config,outdir,project,part)
            BlockWork(name=part,outdir=outdir,project=project,params=func_config,config_id=configid,func=func)
    if len(root_out_dir)==0:
        outdir=""
    else:
        outdir=os.path.abspath(root_out_dir)
    out_intermedia_new(config)
    if stat:
        stat_process(config=config,root_out_dir=root_out_dir,threads=threads)
    else:
        out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir),threads=threads)
    return True





def stat_process(config:dict,root_out_dir="",threads=8):
    for config_id in config.get("config_ids",["DEFAULT"]):
        this_config=config[config_id]

        if len(root_out_dir)==0:
            outdir=os.path.join(os.getcwd(),this_config["outdir"])
        else:
            outdir=os.path.abspath(root_out_dir)
        mkdirs(outdir)

        stat_order=this_config["order_stat"]
        
        for part in stat_order:
            BlockStat(name=part,outdir=outdir,project="STAT",params=this_config["stat"][part],config_id=config_id)
    #out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir),threads=threads)
    if len(root_out_dir)==0:
        outdir=""
    else:
        outdir=os.path.abspath(root_out_dir)
    out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir),threads=threads)
    out_intermedia_new(config)

    print("stat modules is under developing")
    return True