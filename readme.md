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



# Detail

## cli command

## config format

# Advanced

## self-defined functions

## add you own keywords



Any problem, contact me: yang_dongxu@qq.com

