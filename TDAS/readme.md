[TOC]

## basic description
This library uses yaml as a config file, to generate shell command auto. It is not a tool to excute functions, just combine them together

## Advantages vs shell 

* It forces user to follow the rule defined in yaml config, which performs high modularity and low cohension between modules, so more readable and cheaper to re-use code to other works.

* It provides a more humanable way to process params transimission to other scripts user-defined

* It provides a more simple way to process input files, by given a csv file with format user define, but not dirs or paths which is not robust.

## Disadvantages

* More complex than pure shell scripts, but may be overcome by configs defined by author

## Usage

This workflow consists of three subcommands, "generate", "cmd", "stat"

### generate
generate a config file to the path you set with -o, and current workdir if without -o
params:
> -h print help info  
> -n choose the config you want to generate, without suffix.  
> -o the outdir
>> blank: a blank templete for create your own configs    
>> chipseq: a config file to process chipseq pipeline, by bowtie as mapping tools  
>> rnaseq: a config file to process chipseq pipeline, by STAR as mapping tools
>> wgbs_pe: a config file to process paired WGBS, and under testing      

### cmd
part to generate shell command files with config file input.  
Two params are request: -c and -bf.  
-c means config file  in yaml format, but json5 may also supported, though not recommended  
-b means input seq info by hand,  which should followd by -f and filename  
>-a means search files auto, by given path, but not recommend, because little filename is supported and contradict with mine pupose$

### stat
part to run second part of config file, with -c points out the path of config file
> this part may fused into cmd part in future, it's an unstable version

## Format of config file
For the first, it's a yaml file, a convient format for write config by hand.
it has the items below:
> seq_info_format: define the input seqpair file in a list, with the first item is the delim char, and others are columns names, and a column called project should be included. by the way, config_id will be set as DEFAULT if absent in here  
> seq_order: order in the seq pair file you input by -bf, just use numbers as blank config   
> config_ids: the config ids will be process in this config file. Multi config id support is under development

>DEFAULT: the part you define how to process, you may create other names
>> cmd_fusion_order: how to fusion the order together, by the cmd_order set in wrokflow part
>> cmd_name: the output cmd txt name
>> log_name: useless, but keep it by history reason
>> outdir: all outputs will appear in this dir
>> dataname: name to store run infomation, a yaml format file
>> order: order to process workflow,  each step should be contained here, otherwise they will be skipped
>> order_stat: order to process stat part, similar as order item.  
>>workflow: define the detail parts you want to process liki below:

>>>partname:  
>>>   outdir: hello #output of this part, default is the partname
>>>   path: path of the program you want to excute in this part
>>>   cmd_order: the symbol defined in cmd_fusion_order  
>>>   father: dict, define as  [name in this part:[from which part, how it called in the source part outputs]]  
>>>   variables: define variables, use {} to quote variables get from father
>>>   variables_eval: complex ones, can process strings by functions defined in basic_functions.py.
>>>   functions: functions should be excute when the script run, but not the command file run
>>>   params: a key part, define the real body in the outputfile, dict format, with a speical key blank, whose arrributes is a list and will be placed last in the command. NOTICE: \n is needed if you want to use multi lines.
>>>   outparams: params you want to transfer to other parts

Any problems, contact me.
