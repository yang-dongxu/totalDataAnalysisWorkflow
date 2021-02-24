import os
import sys
import logging

from Intermedia import Intermedia
from Block import Block,default_func,mkdirs




class BlockStat(Block):


    def __init__(self,name:str,outdir:str,params:dict,project:str="STAT",config_id="DEFAULT",func=default_func,*args,**kwargs):
        super().__init__(name=name,outdir=outdir,project=project,params=params,*args,**kwargs)

        self.iparams_list=params.get("iparams_list",{})
        self.iparams_single=params.get("iparams_single",{})
 
        self.cmd_part=params.get("cmd_part","STAT")
        self.project=project

        self.process()


    
    def process_iparams(self):
        for item,options in self.iparams_list.items():
            part=options[0]
            attribute=options[1]
            sep=options[2] if len(options)>2 else 0
            value=sep.join(Intermedia.get_attributes_batch(part,attribute))
            self.values[item]=value
        
        for item,options in self.iparams_single.items():
            part=options[0]
            attribute=options[1]
            project=options[2] if len(options)>2 else ""
            value=Intermedia.get_term(part,project,attribute)
            self.values[item]=value
        return 0


