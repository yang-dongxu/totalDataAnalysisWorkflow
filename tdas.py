#!/usr/bin/env python


import os
import sys
import argparse
import json5
import logging
import json
import yaml
import configparser
import pickle

## start to read tdas.ini
SCRIPT_PATH=os.path.join(os.path.split(__file__)[0])
LIBRARY="TDAS"

def parse_config_name(cp:configparser.ConfigParser,name="default"):
    names=os.path.join(SCRIPT_PATH,LIBRARY,cp.get("global",'config_name_list'))
    f=open(names)
    names_list=yaml.safe_load(f)
    f.close()
    if  name in names_list:
        return os.path.join(SCRIPT_PATH,LIBRARY,cp.get("global",'config_dir'),names_list[name])
    else:
        logging.error(f"your config name {name} not in lists {names}, please add them and cp config file to {SCRIPT_PATH}/{LIBRARY}/{cp.options('config_dir')} \n" )
        sys.exit()

ini=os.path.join(SCRIPT_PATH,LIBRARY,"tdas.ini")
CP=configparser.ConfigParser()
CP.read(ini)

VERSION="0.0.1"
DEFAULT_CONFIG=parse_config_name(CP)

script_name=os.path.abspath(__file__)
#LIBRARY='.'
#DEFAULT_CONFIG=os.path.join(SCRIPT_PATH,LIBRARY,"tdas_config.yaml")


from TDAS import parseinput
from TDAS.combine_modules import *
from TDAS.Intermedia import Intermedia

logging.basicConfig(level=logging.WARNING)

def parse_argument(title="sub command",):
    parser=argparse.ArgumentParser()
    sub_parser=parser.add_subparsers(title=title)
    add_generate_config(sub_parser=sub_parser)
    add_cmd(sub_parser=sub_parser)
    add_stat(sub_parser=sub_parser)
    parser.set_defaults(func=parser.print_help)
    return parser

def get_usage():
    usage=f"version: {VERSION}\n to get more help, use -h"
    print(usage)
    sys.exit(0)


def add_generate_config(sub_parser:argparse.ArgumentParser):
    new_parser=sub_parser.add_parser("generate")
    new_parser.add_argument('-n','--name',dest='config_name',type=str,action="store",help="name of config you want to generate",default="default")
    new_parser.add_argument('-o','--outdir',dest="outdir",type=str,action="store",default=os.getcwd())
    new_parser.set_defaults(func=generate_config)
    return True


def add_cmd(sub_parser:argparse.ArgumentParser,default_config=DEFAULT_CONFIG):
    new_parser=sub_parser.add_parser("cmd")

    input_opt=new_parser.add_mutually_exclusive_group()
    input_opt.add_argument('-a','--auto',dest="auto",action="store_true",default=True,help="choose this to let this script get seg pair info with input dir auto. default choose\n")
    input_opt.add_argument('-b','--byhand',dest="byhand",action="store_true",default=False,help='choose this to input seg pair info with a file, which is determine by -f\n')

    new_parser.add_argument('-i','--input_dir',dest="input_dir",type=str,action='store',help="input a dir where fq exists, and the script wiil determine the pair\n")
    new_parser.add_argument('-f','--seqinfo',dest="seqinfo",type=str,action="store",help="input a file with paired seqs, it should be a csv with no head, and contain three columns:project_name,pair1,pair2\n")

    new_parser.add_argument('-o','--outdir',dest="outdir",type=str,action="store",default="",help="output dir")
    new_parser.add_argument('-c','--config',dest="config",type=str,action="store",default=DEFAULT_CONFIG)
    
    new_parser.add_argument('-p','--threads',dest="threads",type=int,action="store",default=1,help="how many tasks can be put in back(&), by shell command wait")
    new_parser.add_argument('-m','--mode',dest="mode",type=int,action="store",default=1,help="out put mode, project-first (0) or part-first (1)")


    new_parser.set_defaults(func=run)
    return True


def add_stat(sub_parser:argparse.ArgumentParser,default_config=DEFAULT_CONFIG):
    new_parser=sub_parser.add_parser("stat")
    input_opt=new_parser.add_mutually_exclusive_group()
    input_opt.add_argument('-a','--auto',dest="auto",action="store_true",default=True,help="choose this to let this script get input intermedia data info from config auto. default choose\n")
    input_opt.add_argument('-b','--byhand',dest="byhand",action="store_true",default=False,help='choose this to input seg pair info with a file, which is determine by -f\n')

    new_parser.add_argument('-f','--intermedia-info',dest="seqinfo",type=str,action="store",help="input a file with paired seqs, it should be a csv with no head, and contain three columns:project_name,pair1,pair2\n")

    new_parser.add_argument('-p','--threads',dest="threads",type=int,action="store",default=1,help="how many tasks can be put in back(&), by shell command wait")
    new_parser.add_argument('-m','--mode',dest="mode",type=int,action="store",default=1,help="out put mode, project-first (0) or part-first (1)")


    new_parser.add_argument('-c','--config',dest="config",type=str,action="store",default=DEFAULT_CONFIG)
    new_parser.set_defaults(func=stat)
    return True

def stat(args):
    #outdir=args.outdir
    config=parse_config(args.config)
    if not args.byhand:
        flag=False
        for configid in config["config_ids"]:
            if configid in config:
                if "outdir" in config[configid]:
                    datapath=os.path.join(os.path.abspath(config[configid]["outdir"]),config[configid]["data_name"])
                    if os.path.exists(datapath):
                        try:
                            with  open(datapath) as f:
                                Intermedia.loads(f)
                                flag=True
                                break
                        except:
                            logging.error(f"intermedia data {datapath} broken!")
        if not flag:
            logging.error("can't find intermedia file auto, please try to point its name")
    else:
        with open(os.path.abspath(args.seqinfo)) as f:
            Intermedia.loads(f.read())
    stat_process(config,threads=args.threads,mode=args.mode)
    
    
    

def generate_config(args):
    config_path=parse_config_name(CP,args.config_name)
    out_name=os.path.abspath(args.outdir)
    cmd="cp {default} {target}".format(default=config_path,target=out_name)
    print(cmd)
    os.system(cmd)
    return True

def parse_config(configname:str)->dict:
    if not os.path.isfile(configname):
        name=parse_config_name(CP,configname)
    else:
        name=os.path.abspath(configname)
    f=open(name,encoding='utf8',errors="ignore")
    logging.info(f"Start to get config file : {name}")
    if name.split(".")[-1]=="json" or name.split(".")[-1]=="json5":
        config=json5.load(f)
    else:
        config=yaml.safe_load(f)
    logging.info(f"Get config file : {name}")
    f.close()
    return config

def run(args):
    outdir=args.outdir
    config=parse_config(args.config)
    if args.byhand:
        seqs=parseinput.parse_inputfile(config,args.seqinfo)
    else:
        seqs=parseinput.parse_inputdir(config,args.input_dir)
    
    logging.info("start processing")
    process(config,outdir,threads=args.threads,mode=args.mode)
    logging.info("processing end")
    logging.info(Intermedia.get_str())

    #print(Intermedia.get_cmd_out(config))
    


if __name__=="__main__":
    parser=parse_argument()
    args=parser.parse_args()
    args.func(args)




