import os
import sys
import logging

from TDAS.Intermedia import Intermedia
from TDAS.Block import Block,default_func,mkdirs



class BlockWork(Block):

    def __init__(self,name:str,outdir:str,params:dict,project:str="STAT",config_id="DEFAULT",func=default_func,*args,**kwargs):
        super().__init__(name=name,outdir=outdir,project=project,params=params,func=func,*args,**kwargs)

        self.iparams=params.get("father",{})
 
        self.process()

    def process_iparams(self):
        for item,options in self.iparams.items():
            part=options[0]
            attribute=options[1]
            value=Intermedia.get_term(part,self.project,attribute)
            self.values[item]=value
        return 0