import os
import sys
import logging

from TDAS.Intermedia import Intermedia

def default_func(block,*args,**kwargs):
    return 0


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return True


def trim(block,*args,**kwargs):
    iseq1=os.path.split(block.values["iseq1"])[-1][:-6]
    iseq2=os.path.split(block.values["iseq2"])[-1][:-6]
    suffix_oseq1="_val_1.fq.gz"
    suffix_oseq2="_val_2.fq.gz"
    outdir=block.values["outdir"]
    if iseq1[-1]=="1":
        oseq1=os.path.join(outdir,iseq1+suffix_oseq1)
        oseq2=os.path.join(outdir,iseq2+suffix_oseq2)
    else:
        oseq1=os.path.join(outdir,iseq2+suffix_oseq1)
        oseq2=os.path.join(outdir,iseq1+suffix_oseq2)

    block.outparams["oseq1"]=oseq1
    block.outparams["oseq2"]=oseq2

SPfucntions={
    "trim":trim,
    "other":default_func
}
