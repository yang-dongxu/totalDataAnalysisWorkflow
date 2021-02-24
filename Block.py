import os
import sys
import logging

from Intermedia import Intermedia

def default_func(cls,*args,**kwargs):
    return 0

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return True



class Block:

    def __init__(self,name:str,outdir:str,project:str,params:dict,config_id="DEFAULT",func=default_func,*args,**kwargs):
        self.name=name
        self.need = params.get("need",False)
        self.path = params.get("path"," ")
        self.iparmas=params.get("iparams",{})
        self.outparams=params.get("outparams",{})
        self.outdir=os.path.join(outdir,params.get("outdir",name))
        self.variables=params.get("variables",{})
        self.params=params.get("params",{})
        self.functions=params.get("functions",[])
        self.functions_last=params.get("functions_last",[])
        self.check_paths=params.get("check_paths",[])
        self.cmd_part=params.get("cmd_part","1")
        self.project=project

        self.sp_func=func
        self.sp_func_args=args
        self.sp_func_kwargs=kwargs

        self.values={}
        self.outparams={}
        self.cmd=""

        Intermedia.add_term(self.name,self.project,"config_id",config_id)
        Intermedia.add_term(self.name,self.project,"need",self.need)

    def process(self):
        self.values["outdir"]=self.outdir
        mkdirs(self.outdir)

        self.process_iparams()

        self.sp_func(self,self.sp_func_args,self.sp_func_kwargs)

        self.process_variables()
        self.process_functions()
        self.process_outparams()
        self.process_checkpath()
        self.process_functions_last()
        
        self.generate_cmd()

    
    def process_iparams(self):
        for item,options in self.iparmas.items():
            part=options[0]
            attribute=options[1]
            project=options[2] if len(options)>2 else ""
            value=Intermedia.get_term(part,project,attribute)
            self.values[item]=value
        return 0
    def process_variables(self):
        for item,value in self.variables.items():
            new_value=str.format_map(value,self.values)
            self.values[item]=new_value
        return 0
    def process_functions(self):
        for func in self.functions:
            exec(str.format_map(func,self.values))
        return 0
    def process_outparams(self):
        for item,value in self.outparams.items():
            new_value=str.format_map(value,self.values)
            Intermedia.add_term(self.name,self.project,item,new_value)
            self.outparams[item]=new_value
        return 0
    def process_functions_last(self):
        for func in self.functions_last:
            exec(str.format_map(func,self.values))
        return 0
    def process_checkpath(self):
        for item in self.check_paths:
            path=str.format_map(item,self.values)
            assert isinstance(path,str)
            assert os.path.exists(path.format_map(locals()))

    def wrap_cmd(self,cmd:str):
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
        for this_key, this_values in self.params.items():
            if this_key=="blank":
                blank_list=this_values
            else:
                if isinstance(this_values,list):
                    values=" ".join(this_values)
                    logging.warning(f"for params, {this_key} has a list values")
                else:
                    values=this_values
                params_list.append("  ".join([str(this_key),str(values)]).format_map(self.values))
        params_list+=[i.format_map(self.values) for i in blank_list]
        cmd_params=" ".join(params_list)

        cmd=f"{self.path} {cmd_params}"
        self.cmd=self.wrap_cmd(cmd)
        Intermedia.add_term(self.name,self.project,"command",self.cmd)
        Intermedia.add_term(self.name,self.project,"command_part",self.cmd_part)

        return self.cmd
    


    def get_cmd(self):
        return self.cmd