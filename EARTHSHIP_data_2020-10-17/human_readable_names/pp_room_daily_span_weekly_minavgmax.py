import os, json
import sys, glob
#from datetime import datetime as dt
#import time
import numpy as np
#from scipy.signal import butter, lfilter, freqz, filtfilt
import matplotlib.pyplot as plt

from postProcessTools import PostProcess

### 
# note: script to produce cleaned-up Wohnzimmer_temperatur_Luft.dat
###
pP = PostProcess()

def make_rfc_gnuplot_readable_file(thefile, header, array):
    print("writing gnuplot readable data file: {}".format(thefile))
    with open(thefile, "w") as out:
        out.write("{}\n".format(header))
        for row,content in enumerate(array):
            try:
                rfctime = pP._transform_float_to_rfc(content[0])
                if array[row][0] - array[row-1][0] < 3600.:
                    out.write("{}    {}\n".format(rfctime,content[1]))
                else:
                    out.write("\n\n{}    {}\n".format(rfctime,content[1]))
            except(IndexError):
                pass

def main():
    title = "Woechentliches MinMax von der taeglichen Schwankung"
    
    input1 = "Wohnzimmer_temperatur_dailyWeekly_intermediate1.dat"
    intermediate_file = "Wohnzimmer_daily_span_weekly_minavgmax_intermediate"
    output1 = "Wohnzimmer_daily_span_weekly_minavgmax.dat"
    
    daily = 24*60*60
    weekly = 7*daily
    zero_time = 12*60*60 + 0*60 + 0
    offset = daily - zero_time
    np1 = np.loadtxt(input1)
    maxI = len(np1)
    start_time = np1[0][0] + offset # set to midnight
    
    if os.path.isfile("{}1.dat".format(intermediate_file)):
        print("Minmax numpy array already written, if you want to reprocess rm {}".format("{}1.dat".format(intermediate_file)))
        np_minmax = np.loadtxt("{}1.dat".format(intermediate_file))
    else:
        print("Step 1: write daily span weekly minmax")
        time = start_time
        i=0
        dminmax = []
        while i < maxI:
            spans=[]
            try:
                while np1[i][0] < time + weekly:
                    span = np1[i][2] - np1[i][1]
                    spans.append(span)
                    i=i+1
                midweek = time +0.5*weekly
                if spans:
                    spanavg = sum(spans) / float(len(spans))
                    spanmin = min(spans)
                    spanmax = max(spans)
                    if spanavg < spanmin: print(midweek,spanmin,spanavg,spanmax, spans)
                    dminmax.append([midweek,spanmin,spanavg,spanmax])
                time = time + weekly
            except(IndexError):
                pass
        np_minmax = np.array(dminmax)
        pP.write_array(np_minmax, outputfilename="{}1.dat".format(intermediate_file))
    
    
    if os.path.isfile("{}".format(output1)):
        print("Already finished writing gnuplot readable file. If you want to re-process, rm {}".format(output1))
    else:    
        print("Step 2: re-write weekly minmax in rfc time, put double newline for measurement leaks, put header")
        with open(output1, "w") as out:
            out.write("# time    weekly_min    weekly_avg    weekly_max  of air-temp_below_ceiling_daily_span (processed with pp_room_daily_span_weekly_minmax.py)\n")
            for row,content in enumerate(np_minmax):
                try:
                    rfctime = pP._transform_float_to_rfc(content[0])
                    if np_minmax[row][0] - np_minmax[row-1][0] < 2*weekly:
                        out.write("{}    {:f}    {:f}    {:f}\n".format(rfctime,content[1],content[2],content[3]))
                    else:
                        out.write("\n\n{}    {:f}    {:f}    {:f}\n".format(rfctime,content[1],content[2],content[3]))
                except(IndexError):
                    pass
  
  
  
  
  
if __name__ == "__main__":
    main()
