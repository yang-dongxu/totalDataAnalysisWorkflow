[TOC]

# Summary

It's a library to generate analysis pipeline by simple yaml-format config file. The command will generate a bash script which could run in anyway you want and as a history log.

# Basic usage

To use this library, you have to to these steps:

* clone this library to your local, by git clone 

* clone another repo named small_tools_of_bioinformatics, which server for this repo, by git clone .

* add a envrionment variable $SCRIPTS= "the repo path". You can add this in .bashrc like below, with you own path instead:

  > export SCRIPTS="/home/user/scripts/small_tools_of_bioinformatics"

* generate a config file you need, which is already created by author. Take chipseq.yamal as example

  ```shell
  python tdas.py generate -n "configname" -o "you destination dir"
  ```
* generate a seqpair table, for example, try.seqpair.table
  > seqpair table is a special table defined here, it describes you raw info. It\'s character-delimter table, with define in the config yaml you choose  
  > Generally, it should contain four columns: project(row name);idir(where you input file is);iseq1(the name of R1 in pair-end seq. can be others if you define it in the yaml);iseq2(R2 fastq.gz name)
* finally, you can get output we want, by command below
    ```shell
    python tdas.py cmd -c chipseq.yaml -bf try.seqpair.table 
    ```
	**by the command, you will get a dir created with name defined in the config yaml, and a bash script is in the dir**, you can treat it in anyway you want. Enjoy your time~


# Advanced

## config format
config file here used is a yaml format file.  
It consists of two parts: head info and process body: 
- In the head part, it defines how your seqpair table look like, order to process each record, and how many config part you can use  
- In the process body, many config part is defined detail.

Config part has three parts: header, workflow, and stat functions.
header part about output info, process order  

**work flow part** defined steps used in head. Each steps will apply to every record in seqpair table, if the step is used in head order module.  

**stats function part** define some post-process steps, such as basic QC summmarise or file-info summary.   
Or you can do anythings you want.   

## self-defined functions

For some complex functions which can't describe by yaml config file, you can add you own process function within the frame we provided here.
see spfunctions.py.   
**Don't forget add self-defined functions to the bottom dicts! **

## add you own keywords

Key words are key-items in the yaml config file. We define the process in Block.py.    
It's a complex work so not suggested. But you are welcome to do this if you really to do so. I am willing to provide helps as your request! 

---
Any problem, contact me: yang_dongxu@qq.com

