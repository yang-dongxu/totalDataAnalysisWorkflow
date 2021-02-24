import os
import sys
import logging

from Intermedia import Intermedia


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return True

    
def default_func(cls,*args,**kwargs):
    return 0


class BlockStat:

    def __init__(self,name:str,outdir:str,params:dict,config_id="DEFAULT",func=default_func,*args,**kwargs):
        self.name=name
        self.need = params.get("need",False)
        self.path = params.get("path"," ")
        self.__iparmas_list=params.get("iparams_list",{})
        self.__iparmas_single=params.get("iparams_single",{})
        self.__outparams=params.get("outparams",{})
        self.__outdir=os.path.join(outdir,params.get("outdir",name))
        self.__variables=params.get("variables",{})
        self.__params=params.get("params",{})
        self.__functions=params.get("functions",[])
        self.__functions_last=params.get("functions_last",[])
        self.__check_paths=params.get("check_paths",[])
        self.__cmd_part=params.get("cmd_part","STAT")
        self.__project="STAT"

        self.sp_func=func
        self.sp_func_args=args
        self.sp_func_kwargs=kwargs

        self.__values={}
        self.outparams={}
        self.cmd=""

        Intermedia.add_term(self.name,self.__project,"config_id",config_id)

        self.__process()

    def __process(self):
        self.__values["outdir"]=self.__outdir
        mkdirs(self.__outdir)

        self.__process_iparams()

        self.sp_func(self,self.sp_func_args,self.sp_func_kwargs)

        self.__process_variables()
        self.__process_functions()
        self.__process_outparams()
        self.__process_checkpath()
        self.__process_functions_last()
        
        self.generate_cmd()

    
    def __process_iparams(self):
        for item,options in self.__iparmas_list.items():
            part=options[0]
            attribute=options[1]
            sep=options[2] if len(options)>2 else 0
            value=sep.join(Intermedia.get_attributes_batch(part,attribute))
            self.__values[item]=value
        
        for item,options in self.__iparmas_single.items():
            part=options[0]
            attribute=options[1]
            project=options[2] if len(options)>2 else ""
            value=Intermedia.get_term(part,project,attribute)
            self.__values[item]=value
        return 0
    def __process_variables(self):
        for item,value in self.__variables.items():
            new_value=str.format_map(value,self.__values)
            self.__values[item]=new_value
        return 0
    def __process_functions(self):
        for func in self.__functions:
            exec(str.format_map(func,self.__values))
        return 0
    def __process_outparams(self):
        for item,value in self.__outparams.items():
            new_value=str.format_map(value,self.__values)
            Intermedia.add_term(self.name,self.__project,item,new_value)
            self.outparams[item]=new_value
        return 0
    def __process_functions_last(self):
        for func in self.__functions_last:
            exec(str.format_map(func,self.__values))
        return 0
    def __process_checkpath(self):
        for item in self.__check_paths:
            path=str.format_map(item,self.__values)
            assert isinstance(path,str)
            assert os.path.exists(path.format_map(locals()))

    def __wrap_cmd(self,cmd:str):
        reptimes=5
        header=f"echo \"{'#'*reptimes} start {self.name} {'#'*reptimes}\" \n"
        footer=f"echo \"{'#'*reptimes} stop {self.name} {'#'*reptimes}\" \n"
        if self.need:
            return header+cmd.strip()+"\n"+footer
        else:
            return header+"#"*2+" "+cmd.strip()+"\n"+footer
    
    def generate_cmd(self):
        blank_list=[]
        params_list=[]
        for this_key, this_values in self.__params.items():
            if this_key=="blank":
                blank_list=this_values
            else:
                if isinstance(this_values,list):
                    __values=" ".join(this_values)
                    logging.warning(f"for params, {this_key} has a list values")
                else:
                    __values=this_values
                params_list.append("  ".join([str(this_key),str(__values)]).format_map(self.__values))
        params_list+=[i.format_map(self.__values) for i in blank_list]
        cmd_params=" ".join(params_list)

        cmd=f"{self.path} {cmd_params}"
        self.cmd=self.__wrap_cmd(cmd)
        Intermedia.add_term(self.name,self.__project,"command",self.cmd)
        Intermedia.add_term(self.name,self.__project,"command_part",self.__cmd_part)

        return self.cmd
    


    def get_cmd(self):
        return self.cmd