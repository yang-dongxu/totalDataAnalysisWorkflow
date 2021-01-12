import logging
import sys
import os
from copy import deepcopy

try:
    from pandas.io.json._normalize import nested_to_record 
except:
    from pandas.io.json.normalize import nested_to_record

class Intermedia:
    __data={}
    
    @classmethod
    def add_parts(cls,part:str):
        if part in cls.__data:
            return cls.__data[part]
        else:
            cls.__data[part]={}
            return True
    
    @classmethod
    def add_project(cls,part:str,project:str):
        cls.add_parts(part)
        if project in cls.__data[part]:
            return cls.__data[part][project]
        else:
            cls.__data[part][project]={}
            return True
    
    @classmethod
    def add_term(cls,part:str=None,project:str=None,term:str=None,value=None,*args):
        if part==None or project==None or term==None or value==None:
            assert len(args)>=4
            part=args[0]
            project=args[1]
            term=args[2]
            value=args[3]
        cls.add_project(part,project)
        cls.__data[part][project][term]=value
        return value
    
    @classmethod
    def get_term(cls,part:str,project:str,term:str):
        try:
            return deepcopy(cls.__data[part][project][term])
        except:
            logging.error(f"no data in {part} {project} {term} ")
            return None
    
    @classmethod
    def get_str(cls):
        return nested_to_record(cls.__data)

    @classmethod
    def get_next_to_process(cls):
        part="raw"
        for project in cls.__data[part]:
            yield part,project,cls.get_term(part,project,"config_id")



    @classmethod
    def iter(cls):
        raw='raw'
        for part,values in cls.__data.items():
            for project,values2 in values.items():
                yield deepcopy(part),deepcopy(project),cls.get_term('raw',project,"config_id")

    @classmethod
    def __get_cmd_out_project_first(cls,config,root_out_dir=""):
        #commands={config_id:{project:{cmd_part:[commands]}}}
        commands={}
        for i in cls.iter():
            part,project,config_id=deepcopy(i)
            command=cls.get_term(part=part,project=project,term="command")
            cmd_part=cls.get_term(part=part,project=project,term="command_part")
            logging.info(f"get command of {config_id} {project} {cmd_part} {part}")
            if config_id in commands:
                if project in commands[config_id]:
                    if cmd_part in commands[config_id][project]:
                        if part in commands[config_id][project][cmd_part]:
                            raise(TypeError(f"duplcate process for {config_id}  {cmd_part} {part} \n"))
                        else:
                            commands[config_id][project][cmd_part][part]=command
                    else:
                        commands[config_id][project][cmd_part]=deepcopy({part:command})
                else:
                    commands[config_id][project]={cmd_part:{part:command}}
            else:
                commands[config_id]={project:{cmd_part:{part:command}}}
        name_to_commands={}
        ##{cmd_name:[cmds]}
        for config_id in commands:
            if len(root_out_dir)==0:
                outdir=os.path.join(os.getcwd(),config[config_id]["outdir"])
            else:
                outdir=root_out_dir
            name=os.path.join(outdir,config[config_id]["cmd_name"])
            orders=config[config_id]["order"]
            cmd_orders = config[config_id]["cmd_fusion_order"]
            #for project in commands[config_id]:
                #for cmd_part in cmd_orders:
            for cmd_part in cmd_orders:
                for project in commands[config_id]:
                    for part in  orders:
                        if cmd_part not in commands[config_id][project]:
                            continue
                        if part not in commands[config_id][project][cmd_part]:
                            continue
                        command=commands[config_id][project][cmd_part][part]
                        if name not in name_to_commands:
                            name_to_commands[name]=[command]
                        else:
                            name_to_commands[name].append(command)
        return name_to_commands

    @classmethod
    def __get_cmd_out_part_first(cls,config):
        #commands={config_id:{cmd_part:{project:[commands]}}}
        commands={}
        for i in cls.get_next_to_process():
            part,project,config_id=i
            command=cls.get_term(part=part,project=project,term="command")
            cmd_part=cls.get_term(part=part,project=project,term="command_part")
            if config_id in commands:
                if cmd_part in commands:
                    if project in commands[config_id][cmd_part]:
                        commands[config_id][cmd_part][project].append(command)
                    else:
                        commands[config_id][cmd_part][project]=[command]
                else:
                    commands[config_id][cmd_part]={project:[command]}
            else:
                commands[config_id]={cmd_part:{project:[command]}}
        return commands
            
    @classmethod
    def get_cmd_out(cls,config,root_out_dir="",project_first=True):
        if project_first:
            return cls.__get_cmd_out_project_first(config,root_out_dir=root_out_dir)
        

    @classmethod
    def get_attributes_batch(cls,part,attributes):
       projects=list(cls.__data[part].keys())
       for project in projects:
           yield cls.get_term(part=part,project=project,term=attributes)
