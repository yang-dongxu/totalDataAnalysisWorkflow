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
     

def process(config:dict,outdir:str):
    for i in Intermedia.get_next_to_process():
        raw,project,configid=i
        this_config=config[configid]
        for part in this_config["order"]:
            partname=part.strip().split("/")[0]
            func=METHOD[partname]
            func_config=this_config["workflow"][part]
            func(func_config,outdir,project,part)