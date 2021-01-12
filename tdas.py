#!/usr/bin/env python


import os
import sys
import argparse
import json5
import logging
import json
import yaml
import configparser

## start to read tdas.ini
SCRIPT_PATH=os.path.join(os.path.split(__file__)[0])

def parse_config_name(cp:configparser.ConfigParser,name="default"):
    names=os.path.join(SCRIPT_PATH,cp.get("global",'config_name_list'))
    f=open(names)
    names_list=yaml.safe_load(f)
    f.close()
    if  name in names_list:
        return os.path.join(SCRIPT_PATH,cp.get("global",'config_dir'),names_list[name])
    else:
        logging.error(f"your config name {name} not in lists {names}, please add them and cp config file to {SCRIPT_PATH}/{cp.options('config_dir')} \n" )
        sys.exit()

ini=os.path.join(SCRIPT_PATH,"tdas.ini")
CP=configparser.ConfigParser()
CP.read(ini)

VERSION="0.0.1"
DEFAULT_CONFIG=parse_config_name(CP)

script_name=os.path.abspath(__file__)
#LIBRARY='.'
#DEFAULT_CONFIG=os.path.join(SCRIPT_PATH,LIBRARY,"tdas_config.yaml")


import parseinput
from combine_modules import *
from Intermedia import Intermedia

logging.basicConfig(level=logging.WARNING)

def parse_argument(title="sub command",):
    parser=argparse.ArgumentParser()
    sub_parser=parser.add_subparsers(title=title)
    add_generate_config(sub_parser=sub_parser)
    add_run(sub_parser=sub_parser)
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


def add_run(sub_parser:argparse.ArgumentParser,default_config=DEFAULT_CONFIG):
    new_parser=sub_parser.add_parser("run")

    input_opt=new_parser.add_mutually_exclusive_group()
    input_opt.add_argument('-a','--auto',dest="auto",action="store_true",default=True,help="choose this to let this script get seg pair info with input dir auto. default choose\n")
    input_opt.add_argument('-b','--byhand',dest="byhand",action="store_true",default=False,help='choose this to input seg pair info with a file, which is determine by -f\n')

    new_parser.add_argument('-i','--input_dir',dest="input_dir",type=str,action='store',help="input a dir where fq exists, and the script wiil determine the pair\n")
    new_parser.add_argument('-f','--seqinfo',dest="seqinfo",type=str,action="store",help="input a file with paired seqs, it should be a csv with no head, and contain three columns:project_name,pair1,pair2\n")

    new_parser.add_argument('-o','--outdir',dest="outdir",type=str,action="store",default="",help="output dir")
    new_parser.add_argument('-c','--config',dest="config",type=str,action="store",default=DEFAULT_CONFIG)
    new_parser.set_defaults(func=run)
    return True



def generate_config(args):
    config_path=parse_config_name(CP,args.config_name)
    out_name=os.path.abspath(args.outdir)
    cmd="cp {default} {target}".format(default=config_path,target=out_name)
    print(cmd)
    os.system(cmd)
    return True

def parse_config(configname:str)->dict:
    if not os.path.exists(configname):
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
    process(config,outdir)
    logging.info("processing end")
    logging.info(Intermedia.get_str())

    #print(Intermedia.get_cmd_out(config))
    


if __name__=="__main__":
    parser=parse_argument()
    args=parser.parse_args()
    args.func(args)




