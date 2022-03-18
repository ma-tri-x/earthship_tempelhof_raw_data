#!/bin/python

import os,sys,json,glob,shutil

files = glob.glob('*.dat')

d={}
with open('Rename.json','r') as R:
    d = json.load(R)
    
if not os.path.isdir("./human_readable_names"):
    os.system('mkdir human_readable_names')

for f in files:
    name = f.split('.dat')[0]
    if name in d:
        print("copying {} to {}".format(f,d[name]))
        shutil.copyfile(f,"human_readable_names/{}.dat".format(d[name]))
        
