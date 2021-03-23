import sys
import os

from pandas.io.json._normalize import nested_to_record 
import yaml

from TDAS.Intermedia import Intermedia
from TDAS.functions import *
from TDAS.stats_functions import BlockStat
from TDAS.working_functions import BlockWork
from TDAS.spfunctions import SPfucntions

METHOD={
    "trim":trim,
    "STAR":star,
    "featureCounts":featureCounts,
    "format":format,
    "redistribute":redistribute,
    "other":self_func

} 
     
def out_bash_cmd(cmds):
    for name in cmds:
        if os.path.exists(name):
                os.remove(name)
    for name,cmd in cmds.items():
        mkdirs(os.path.split(name)[0])
        with open(name,'a+') as f:
            f.write("\n".join(cmd))
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

def process_old(config:dict,root_out_dir=""):
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
            if partname in METHOD:
                func=METHOD[partname]
            else:
                func=METHOD["other"]
            func_config=this_config["workflow"][part]
            func(func_config,outdir,project,part)
    if len(root_out_dir)==0:
        outdir=""
    else:
        outdir=os.path.abspath(root_out_dir)
    out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir))
    for i in Intermedia.get_next_to_process(config):
        project,configid=i
        name=os.path.join(config[configid]["outdir"],config[configid]["data_name"])
        out_intermedia(name)

def process(config:dict,root_out_dir=""):
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
    out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir))
    out_intermedia_new(config)




def stat_process(config:dict,root_out_dir=""):
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
    out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir))
    if len(root_out_dir)==0:
        outdir=""
    else:
        outdir=os.path.abspath(root_out_dir)
    out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir))
    out_intermedia_new(config)

    print("stat modules is under developing")