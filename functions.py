import os
import sys
import logging

from copy import deepcopy
from Intermedia import Intermedia

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return True


def paste_params(params:dict):
    params_list=[]
    for key,value in params.items():
        params_list.append("  ".join([key,value]))
    return " ".join(params_list)

def paset_modifi_params(params,values:dict):
    params=deepcopy(params)
    params_list=[]
    for this_key, this_values in params.items():
        params_list.append("  ".join([str(this_key),str(this_values)]).format_map(values))
    return " ".join(params_list)

def get_father_params_command(sources:dict,project:str):
    for varName,param in sources.items():
        assert len(param)==2
        this_part=param[0]
        this_key=param[1]
        cmd=f'{varName}=Intermedia.get_term("{this_part}","{project}","{this_key}")'
        yield cmd

def get_variables_command(sources:dict,project:str):
    for varName,param in sources.items():
        yield f"{varName} = \"{param}\""


def wrap_cmd(cmd:str,project:str,part:str,need:bool=True):
    reptimes=5
    header=f"echo \"{'#'*reptimes} start {project} {part}  {'#'*reptimes}\" \n"
    footer=f"echo \"{'#'*reptimes} stop {project} {part}  {'#'*reptimes}\" \n"
    if need:
        return header+cmd.strip()+"\n"+footer
    else:
        return header+"#"*2+" "+cmd.strip()+"\n"+footer

    
def regular_pipeline(config,part,project,outdir):
    ##set variables from config or father
    part=part
    project=project
    software=config["path"]
    params=config["params"]
    outdir=os.path.join(outdir,config["outdir"])    
    for cmd in get_father_params_command(config["father"],project):
        exec(cmd)
    
    if "variables" in config:
        for cmd in get_variables_command(config["variables"],project):
            exec(cmd)
    
    ##add self-defined names to intermedia
    if "outparams" in config:
        for cmd in get_variables_command(config["outparams"],project):
            exec(cmd)
        for term,value in config["outparams"].items():
            Intermedia.add_term(part=part,project=project,term=term,value=value)

    ##set outdir
    mkdirs(outdir)

    ##generate cmd
    cmd=f"{software} {paset_modifi_params(params=params,values=locals())} "
    cmd=wrap_cmd(cmd,project,part,config["need"])
    #print(cmd)

    ##check path
    for path in config["check_paths"]:
        assert isinstance(path,str)
        assert os.path.exists(path.format_map(locals()))
    

    ##add command and command part id to intermedia
    cmd_part=config["cmd_part"]
    need=config["need"]
    Intermedia.add_term(part=part,project=project,term="command",value=cmd)
    Intermedia.add_term(part=part,project=project,term="command_part",value=cmd_part)
    Intermedia.add_term(part=part,project=project,term="need",value=need)

    
    return cmd,cmd_part,locals()


def trim(config:dict,outdir:str,project:str,part:str="trim"):

    cmd,cmd_part,variables=regular_pipeline(config=config,part=part,project=project,outdir=outdir)

    ##store values to Intermedia
    iseq1=os.path.split(variables["iseq1"])[-1]
    iseq2=os.path.split(variables["iseq2"])[-1]
    suffix_oseq1="_val_1.fq.gz"
    suffix_oseq2="_val_2.fq.gz"
    outdir=variables["outdir"]
    if iseq1[:-6][-1]=="1":
        oseq1=os.path.join(outdir,iseq1+suffix_oseq1)
        oseq2=os.path.join(outdir,iseq2+suffix_oseq2)
    else:
        oseq1=os.path.join(outdir,iseq2+suffix_oseq1)
        oseq2=os.path.join(outdir,iseq1+suffix_oseq2)


    Intermedia.add_term(part=part,project=project,term="oseq1",value=oseq1)
    Intermedia.add_term(part=part,project=project,term="oseq2",value=oseq2)
    Intermedia.add_term(part=part,project=project,term="outdir",value=outdir)

    return cmd,cmd_part

    
def star(config:dict,outdir:str,project:str,part:str="STAR"):
    cmd,cmd_part,variables=regular_pipeline(config=config,part=part,project=project,outdir=outdir)

    ##store values to Intermedia
    iseq1=variables["iseq1"]
    iseq2=variables["iseq2"]
    outdir=variables["outdir"]

    outprefix=config["params"]["--outFileNamePrefix"].format_map(variables)
    mkdirs(os.path.split(outprefix)[0])
    obam_sorted=outprefix+"Aligned.sortedByCoord.out.bam"
    ologfinalout=outprefix+"Log.final.out"
    ologout=outprefix+"Log.out"
    ologprogressout=outprefix+"Log.progress.out"
    osj=outprefix+"SJ.out.tab"

    Intermedia.add_term(part=part,project=project,term="iseq1",value=iseq1)
    Intermedia.add_term(part=part,project=project,term="iseq2",value=iseq2)
    Intermedia.add_term(part=part,project=project,term="obam_sorted",value=obam_sorted)
    Intermedia.add_term(part=part,project=project,term="ologfinalout",value=ologfinalout)
    Intermedia.add_term(part=part,project=project,term="ologout",value=ologout)
    Intermedia.add_term(part=part,project=project,term="ologprogressout",value=ologprogressout)
    Intermedia.add_term(part=part,project=project,term="osj",value=osj)

    return cmd,cmd_part

def featureCounts(config:dict,outdir:str,project:str,part:str="featureCounts"):
    cmd,cmd_part,variables=regular_pipeline(config=config,part=part,project=project,outdir=outdir)

    ibam=variables["ibam"]
    outprefix=config["params"]["-o"].format_map(variables)
    ofeatures=outprefix
    osummary=outprefix+".summary"
    obam=ibam+".featureCounts.bam"
    outdir=variables["outdir"]

    Intermedia.add_term(part=part,project=project,term="ibam",value=ibam)
    Intermedia.add_term(part=part,project=project,term="ofeatures",value=ofeatures)
    Intermedia.add_term(part=part,project=project,term="osummary",value=osummary)
    Intermedia.add_term(part=part,project=project,term="obam",value=obam)

    return cmd,cmd_part


def format(config:dict,outdir:str,project:str,part:str="format"):
    cmd,cmd_part,variables=regular_pipeline(config=config,part=part,project=project,outdir=outdir)
    outdir=variables["outdir"]

    ibam=variables["ibam"]
    osam=config["params"][">"].format_map(variables)

    Intermedia.add_term(part=part,project=project,term="ibam",value=ibam)
    Intermedia.add_term(part=part,project=project,term="osam",value=osam)

    return cmd,cmd_part

def redistribute(config:dict,outdir:str,project:str,part:str="redistribute"):
    cmd,cmd_part,variables=regular_pipeline(config=config,part=part,project=project,outdir=outdir)
    outdir=variables["outdir"]

    isam=variables["isam"]
    otab=config["params"]["-n"].format_map(variables)
    Intermedia.add_term(part=part,project=project,term="isam",value=isam)
    Intermedia.add_term(part=part,project=project,term="otab",value=otab)


    return cmd,cmd_part

