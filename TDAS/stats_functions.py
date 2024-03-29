import os
import sys
import logging

from TDAS.Intermedia import Intermedia
from TDAS.Block import Block,default_func,mkdirs




class BlockStat(Block):


    def __init__(self,name:str,outdir:str,params:dict,project:str="STAT",func=default_func,*args,**kwargs):
        __source = params.get("__source",project)
        self.__source = f"{__source}" # define the stat inherited from which config, and merge them
        super().__init__(name=name,outdir=outdir,project=project,params=params,*args,**kwargs)
        Intermedia.add_term(self.name, "STAT", "__source", __source)

        self.iparams_list=params.get("iparams_list",{})
        self.iparams_single=params.get("iparams_single",{})
 
        self.cmd_part=params.get("cmd_part","STAT")
        self.process()


    
    def process_iparams(self):
        for item,options in self.iparams_list.items():
            part=options[0]
            attribute=options[1]
            sep=options[2] if len(options)>2 else 0
            value=sep.join(Intermedia.get_attributes_batch(part,attribute.format_map(self.values), select_source_id = self.__source))
            self.values[item]=value
        
        for item,options in self.iparams_single.items():
            part=options[0]
            attribute=options[1]
            project=options[2] if len(options)>2 else ""
            value=Intermedia.get_term(part,project,attribute)
            if not value:
                value=list(set(Intermedia.get_attributes_batch(part,attribute.format_map(self.values))),select_source_id = self.__source)[0]
            self.values[item]=value
        return 0
