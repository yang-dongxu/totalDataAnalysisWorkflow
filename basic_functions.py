import os
import sys

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return True

def split(string:str,sep:str="_",index=0):
    '''return i th part of string split by sep'''
    return string.split(sep)[index]

def relpath(path,start):
    return os.path.relpath(path,start)