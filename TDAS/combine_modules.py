import logging
import sys
import os
import re
from copy import deepcopy

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
    if re.search("[^&]&[^&\d]",cmd) and cmd[0] != "#":
        return 1
    else:
        return 0
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

def out_intermedia_new(config):
    def out_intermedia(name):
        with open (name,'w') as f:
            f.write(Intermedia.dumps())
        return True  
    for i in Intermedia.get_next_to_process(config):
        project,configid=i
        name=os.path.join(config[configid]["outdir"],config[configid]["data_name"])
        out_intermedia(name)
    return True  


def process(config:dict,root_out_dir="",stat=True,threads=8,mode=0,**kwargs):
    project_num=0
    for i in Intermedia.get_next_to_process(config):
        project,configid=i
        project_num+=1
        if configid in config:
            this_config=config[configid]
            this_config["__source"] = configid
        else:
            this_config = deepcopy(config["DEFAULT"])
            config[configid] = this_config
            this_config["__source"] = "DEFAULT"
            logging.warning("config_id: {} do not exist in config file, using DEFAULT config instead!".format(configid))
        for attr in ["cmd_name","outdir","data_name","cmd_fusion_order","order","order_stat","workflow","stat"]:
            if attr not in this_config:
                this_config[attr]=config["DEFAULT"][attr]
        if len(root_out_dir)==0:
            outdir=os.path.join(os.getcwd(),this_config["outdir"])
        else:
            outdir=os.path.abspath(root_out_dir)
        mkdirs(outdir)


        if "order" in this_config:
            orders=this_config["order"]
        elif "order" in config["DEFAULT"]:
            orders=config["DEFAULT"]
        else:
            logging.error('you config file is broken! "order" term is needed! ')

        #start to itereach part
        for part in orders:
            partname=part.strip().split("/")[0]
            if partname in SPfucntions: ## determine whether to process by pre-defined functions
                func=SPfucntions[partname]
            else:
                func=SPfucntions["other"]
            if "workflow" in this_config and part in this_config["workflow"]: ## using part defined in the config
                func_config=this_config["workflow"][part]
            elif part in config["DEFAULT"]["workflow"]: ## using part defined in DEFAULT config
                func_config=config["DEFAULT"]["workflow"][part]
            else:
                logging.error(f"the part : {part} do not exist in config: {configid} and DEFAULT! ")
                sys.exit(1)
            #func(func_config,outdir,project,part)
            BlockWork(name=part,outdir=outdir,project=project,params=func_config,config_id=configid,func=func,**kwargs)
    if len(root_out_dir)==0:
        outdir=""
    else:
        outdir=os.path.abspath(root_out_dir)
    threads=min(threads,project_num)
    out_intermedia_new(config)
    if stat:
        stat_process(config=config,root_out_dir=root_out_dir,threads=threads,mode=mode,**kwargs)
    else:
        out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir,mode=mode),threads=threads)
    return True



def stat_process(config:dict,root_out_dir="",threads=8,mode=0,**kwargs):
    for config_id in config.get("config_ids",["DEFAULT"]):
        if config_id in config:
            this_config=config[config_id]
            # this_config["__source"] = config_id # assigned from above process function
            print("config_id: {} exist in config file!".format(config_id) )
        else:
            this_config = deepcopy(config["DEFAULT"])
            this_config["__source"] = "DEFAULT"
            config[config_id] = this_config
            logging.warning("config_id: {} do not exist in config file, using DEFAULT config instead!".format(config_id))

        for attr in ["cmd_name","outdir","data_name","cmd_fusion_order","order","order_stat","workflow","stat"]:
            if attr not in this_config:
                this_config[attr]=config["DEFAULT"][attr]

        if len(root_out_dir)==0:
            outdir=os.path.join(os.getcwd(),this_config["outdir"])
        else:
            outdir=os.path.abspath(root_out_dir)
        mkdirs(outdir)

        stat_order=this_config["order_stat"]

        if "order" in this_config:
            stat_order=this_config["order_stat"]
        elif "order" in config["DEFAULT"]:
            stat_order=config["DEFAULT"]["order_stat"]
        else:
            logging.error('you config file is broken! "order" term is needed! ')

        for part in stat_order:
            if "stat" in this_config and part in this_config["stat"]:
                func_config=this_config["stat"][part]
                func_config["__source"] = this_config["__source"]
            elif part in config["DEFAULT"]["stat"]:
                func_config=config["DEFAULT"]["stat"][part]
                func_config["__source"] = "DEFAULT"
            else:
                logging.error(f"the part : {part} do not exist in config: {config_id} and DEFAULT! ")
                sys.exit(1)
            BlockStat(name=part,outdir=outdir,project="STAT",params=func_config,config_id=config_id, select_source_id = func_config["__source"],**kwargs)
    #out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir),threads=threads)
    if len(root_out_dir)==0:
        outdir=""
    else:
        outdir=os.path.abspath(root_out_dir)
    out_bash_cmd(Intermedia.get_cmd_out(config,root_out_dir=outdir,mode=mode),threads=threads)
    out_intermedia_new(config)

    return True