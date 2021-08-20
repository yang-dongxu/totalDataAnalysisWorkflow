import logging
import sys
import os
import pandas as pd
from copy import deepcopy
#from totalDataAnalysisWorkflow.TDAS.Block import default_func
import yaml

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
        if term !="config_id":
            try:
                return deepcopy(cls.__data[part][project][str(term)])
            except:
                logging.error(f"no data in {part} {project} {term} ")
                return None
        else:
            try:
                if term in cls.__data[part][project]:
                    return cls.__data[part][project][str(term)]
                else :
                    return cls.__data["raw"][project][str(term)]
            except:
                logging.error(f"no data in {part} {project} {term} ")
                return None
    
    @classmethod
    def get_str(cls):
        return nested_to_record(cls.__data)

    @classmethod
    def get_next_to_process(cls,config):
        part="raw"
        seqs=[]
        for project in cls.__data[part]:
            seqs.append( (project,cls.get_term(part,project,"config_id"),cls.get_term(part,project,"seq_order")))
        if "seq_order" not in config:
            seqs.sort(key=lambda x:int(x[2]))
        else:
            if "seq_order"  in config["seq_info_format"]:
                orders=[str(i) for i in config["seq_order"]]
            else:
                orders=list(range(1000))
            try:
                seqs.sort(key=lambda x: orders.index(x[2]))
            except:
                for i in seqs:
                    if i[2] not in orders:
                        logging.error(f"{i[0]} has a undefined seq order {i[2]}, check it!\n")
        for i in seqs:
            yield i[0], i[1]



    @classmethod
    def iter(cls,config):
        raw='raw'
        seqs=[]
        for part,values in cls.__data.items():
            for project,values2 in values.items():
                seqs.append( (deepcopy(part),deepcopy(project),cls.get_term(part,project,"config_id"),cls.get_term("raw",project,"seq_order")))
        if "seq_order" not in config:
            seqs.sort(key=lambda x:int(x[2]))
        else:
            orders=[str(i) for i in config["seq_order"]]
            try:
                seqs.sort(key=lambda x: orders.index(x[-1]))
            except:
                for i in seqs:
                    if i[-1] not in orders:
                        logging.error(f"{i[1]} has a undefined order {i[-1]}, check it!\n")
        for i in seqs:
            yield i[0], i[1], i[2]

    @classmethod
    def iter_raw(cls):
        raw="raw"
        seqs=[]
        for project in cls.__data[raw]:
            seqs.append( (project,cls.get_term(raw,project,"config_id"),cls.get_term(raw,project,"seq_order")))
        return seqs
    
    @classmethod
    def __prepare_cmd_out(cls,config,root_out_dir=""):
        commands=[]
        seq_infos=cls.iter_raw()

        if "seq_order" in config["seq_info_format"]:
            seq_orders=[str(i) for i in config["seq_order"]]
            #print(seq_orders)
        else:
            seq_orders=list(range(1000))

        for config_id in config["config_ids"]:
            if config_id not in config:
                continue
            this_config=config[config_id]
            orders=this_config["order"] if "order" in this_config else config["DEFAULT"]["order"]
            stat_orders=this_config["order_stat"] if "order_stat" in this_config else config["DEFAULT"]["order_stat"]
            #cmd_name=this_config["cmd_name"]
            if len(root_out_dir)==0:
                o=config[config_id]["outdir"] if "outdir" in config[config_id] else config["DEFAULT"]["outdir"]
                outdir=os.path.join(os.getcwd(),o)
            else:
                outdir=root_out_dir
            cmd_name=os.path.join(outdir,this_config["cmd_name"])
            cmd_parts=[str(i) for i in this_config["cmd_fusion_order"]]

            for seq_info in [i for i in seq_infos if i[1] == config_id]:
                project,_,seq_order=seq_info
                #print(seq_info)
                c=cls.get_term("raw",project,"config_id")
                if c!= config_id:
                    continue
                for part in orders:
                    
                    command=cls.get_term(part,project,"command")
                    cmd_part=str(cls.get_term(part,project,"command_part"))
                    try:
                        assert cmd_part in cmd_parts
                    except:
                        logging.error(f"{part} in {config_id} has undefined cmd_part, SKIP!")
                        continue
                    assert seq_order in seq_orders
                    order=orders.index(part)
                    command_attribute={"command":command,"order":order,"config_id":config_id,"project":project,"cmd_part":cmd_parts.index(cmd_part),"seq_order":seq_orders.index(seq_order),"part":part,"name":cmd_name}
                    commands.append(command_attribute)

            for part in stat_orders:
                project="STAT"
                command=cls.get_term(part,project,"command")
                cmd_part=str(cls.get_term(part,project,"command_part"))
                order=stat_orders.index(part)+len(orders)
                try:
                    assert cmd_part in cmd_parts
                except:
                    logging.error(f"{part} in {config_id} has undefined cmd_part, SKIP!")
                    continue
                command_attribute={"command":command,"order":order,"config_id":config_id,"project":project,"cmd_part":cmd_parts.index(cmd_part),"seq_order":seq_orders[-1],"part":part,"name":cmd_name}
                commands.append(command_attribute)
        #print(commands)
        df_commands=pd.DataFrame([pd.Series(i) for i  in commands])
        df_commands=df_commands.drop_duplicates(subset=list(df_commands.columns).remove("config_id")).reset_index(drop=True)
        #print(df_commands.to_csv(sep="\t"))
        return deepcopy(df_commands)
    
    @classmethod
    def __get_cmd_out_project_first(cls,config,root_out_dir=""):
        logging.warning("project first setted! Beware of backgroup settings!")
        commands=cls.__prepare_cmd_out(config,root_out_dir)
        commands=commands.sort_values(["config_id","cmd_part","seq_order","project","order","part"])
        #commands.sort(key=lambda x: (x["config_id"],x["cmd_part"],x["seq_order"],x["project"],x["order"],x["part"]))
        #print(pd.DataFrame(commands).to_csv(sep="\t"))
        #return [(i["name"],i["command"]) for i in commands]
        return list(zip(commands["name"],commands["command"]))
    
    @classmethod
    def __get_cmd_out_part_first(cls,config,root_out_dir=""):
        commands=cls.__prepare_cmd_out(config,root_out_dir)
        commands=commands.sort_values(["config_id","cmd_part","order","seq_order","project","part"])
        #commands.sort(key=lambda x: (x["config_id"],x["cmd_part"],x["order"],x["seq_order"],x["project"],x["part"]))
        #return [(i["name"],i["command"]) for i in commands]
        commands.to_csv(sep="\t")
        return list(zip(commands["name"],commands["command"]))
    
    

    @classmethod
    def __get_cmd_out_project_first_old(cls,config,root_out_dir=""):
        #commands={config_id:{project:{cmd_part:[commands]}}}
        commands={}
        for i in cls.iter(config):
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
            orders=config[config_id]["order"]+config[config_id]["order_stat"]
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
    def get_cmd_out(cls,config,root_out_dir="",mode=0):
        project_first=False
        if mode==0:
            project_first=True
        if project_first:
            commands= cls.__get_cmd_out_project_first(config=config,root_out_dir=root_out_dir)
        else:
            commands=cls.__get_cmd_out_part_first(config=config,root_out_dir=root_out_dir)
        results={}

        for name in list(set([i[0] for i in commands])):
            results[name]=[]
            
        for info in commands:
            name,cmd=info
            results[name].append(cmd)
        return results
        

    @classmethod
    def get_attributes_batch(cls,part,attributes,with_project=False):
        projects=list(cls.__data[part].keys())
        for project in projects:
            if not with_project:
                yield cls.get_term(part=part,project=project,term=attributes)
            else:
                yield cls.get_term(part=part,project=project,term=attributes),project


    @classmethod
    def dumps(cls):
        logging.info("dumps out intermedia info")
        return yaml.safe_dump(cls.__data)
    
    @classmethod
    def loads(cls,data):
        logging.warn("intermedia loads outer info in!")
        cls.__data=yaml.safe_load(data)
        
