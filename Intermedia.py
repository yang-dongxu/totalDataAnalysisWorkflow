import sys
import os

from pandas.io.json._normalize import nested_to_record 


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
        return cls.__data[part][project][term]
    
    @classmethod
    def get_str(cls):
        return nested_to_record(cls.__data)

    @classmethod
    def get_next_to_process(cls):
        part="raw"
        for project in cls.__data[raw]:
            yield raw,project,cls.get_term(raw,project,"config_id")

    @classmethod
    def __get_cmd_out_project_first(cls,config):
        #commands={project:{cmd_part:[commands]}}
        commands={}
        for i in cls.get_next_to_process():
            part,project,config_id=i
            command=cls.get_term(part=part,project=project,term="command")
            cmd_part=cls.get_term(part=part,project=project,term="command_part")
            if project in commands:
                if cmd_part in commands[project]:
                    commands[project][cmd_part].append(command)
                else:
                    commands[project][cmd_part]=[command]
            else:
                command[project]={cmd_part:[command]}
        return commands

    @classmethod
    def __get_cmd_out_part_first(cls,config):
        #commands={cmd_part:{project:[commands]}}
        commands={}
        for i in cls.get_next_to_process():
            part,project,config_id=i
            command=cls.get_term(part=part,project=project,term="command")
            cmd_part=cls.get_term(part=part,project=project,term="command_part")
            if cmd_part in commands:
                if project in commands[project]:
                    commands[cmd_part][project].append(command)
                else:
                    commands[cmd_part][project]=[command]
            else:
                command[cmd_part]={project:[command]}
        return commands
            
    @classmethod
    def get_cmd_out(cls,config,project_first=True):
        if project_first:
            return cls.__get_cmd_out_project_first(config)
        


   