import os
import sys
import logging

from TDAS.Intermedia import Intermedia
from TDAS.basic_functions import *

def default_func(cls,*args,**kwargs):
    return 0



class Block:

    def __init__(self,name:str,outdir:str,project:str,params:dict,config_id="DEFAULT",func=default_func,*args,**kwargs):
        self.name=name
        self.other_args=kwargs
        self.need = params.get("need",False)
        self.path = params.get("path"," ")
        self.iparams=params.get("iparams",{})
        self.outparams=params.get("outparams",{})
        self.outdir=os.path.join(outdir,params.get("outdir",name)).format(project=project)
        self.variables=params.get("variables",{})
        self.variables_eval=params.get("variables_eval",{})
        self.params=params.get("params",{})
        self.functions=params.get("functions",[])
        self.functions_last=params.get("functions_last",[])
        self.check_paths=params.get("check_paths",[])
        self.cmd_part=params.get("cmd_part","1")
        self.project=project

        self.overwrite=params.get("overwrite",True) ### whether to overwrite exist file,default is true if you want choose --overwrite option
        self.overwrite_check=params.get("overwrite_check",[])

        self.sp_func=func
        self.sp_func_args=args
        self.sp_func_kwargs=kwargs

        self.values={}
        self.cmd=""
        self.values["outdir"]=self.outdir
        self.values["outdir_relative"]=params.get("outdir",name)
        self.values["project"]=self.project
        self.values["part"]=self.name

        Intermedia.add_term(self.name,self.project,"config_id",config_id)
        Intermedia.add_term(self.name,self.project,"need",self.need)

    def process(self):
        
        mkdirs(self.outdir)

        self.process_iparams()

        self.sp_func(self,self.sp_func_args,self.sp_func_kwargs)

        self.process_variables()
        self.process_variables_eval()
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
            new_value=str.format_map(str(value),self.values)
            self.values[item]=new_value
        return 0

    def process_variables_eval(self):
        for item,value in self.variables_eval.items():
            new_value=eval(str.format_map(str(value),self.values))
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

    def process_overwrite(self,cmd):
        overwrite_opt=self.other_args["all_args"].overwrite ## set in options
        overwrite=self.overwrite ## set in configs
        overwrite_check=self.overwrite_check
        
        def check_paths(self,checks,cmd):
            ochecks=[]
            if len(checks)==0:
                logging.warning(f" Part: {self.name} No path need check for overwrite ! infer from outparams!")
                ochecks=list(self.outparams.values())
                ochecks=[str.format_map(i,self.values) for i in ochecks]

                logging.warning(f" infered overwrite checked paths: {ochecks}")
            else:
                ochecks=checks
                ochecks=[str.format_map(i,self.values) for i in ochecks]

                logging.info(f"paths need to check for overwrite: {ochecks}")
            ochecks=[f" -e {i} " for i in ochecks]
            if len(ochecks):
                ocmd=f''' if [[ ! ({' || '.join(ochecks)}) ]]; then {cmd}; fi '''
            return ocmd

        if  not overwrite_opt:
            logging.info("## No overwrite allowed. if you want to allow overwrite, check --overwrite options")
            return check_paths(self,overwrite_check,cmd) ### 
        else:
            if not overwrite:
                return check_paths(self,overwrite_check,cmd)
            else: ## want to overwrite
                logging.warning(f"You choose to overwrite in the part {self.name} ")
                return cmd
        return cmd

    def wrap_cmd(self,cmd:str):
        reptimes=5
        project=self.values["project"]
        header=f"echo \"{'#'*reptimes} start {self.name} {project} at TIME `date +'%D %T'` {'#'*reptimes}\" && "
        footer=f"echo \"{'#'*reptimes} stop {self.name} {project} at TIME `date +'%D %T'` {'#'*reptimes}\" "
        if len(cmd.strip()) == 0 :
            return " \n"

        if cmd.strip().endswith("&") and not cmd.strip().endswith("&&") :
            backend=True
            cmd=cmd.strip()[:-1]
        else:
            backend=False

        cmd=self.process_overwrite(cmd)

        if self.need :
            ocmd = header+cmd.strip()+" && "+footer
        else:
            ocmd = header+"#"*2+" "+cmd.strip()+"\n"+footer
        if backend:
            ocmd = f"{ocmd} & \n"
        else:
            ocmd = f"{ocmd} \n"
        return ocmd
    
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
                params_list.append("  ".join([str(this_key),str(values)]).format(**self.values))
        params_list+=[i.format_map(self.values) for i in blank_list]
        cmd_params=" ".join(params_list)

        cmd=f"{self.path} {cmd_params}"
        self.cmd=self.wrap_cmd(cmd)
        Intermedia.add_term(self.name,self.project,"command",self.cmd)
        Intermedia.add_term(self.name,self.project,"command_part",self.cmd_part)

        return self.cmd
    


    def get_cmd(self):
        return self.cmd