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
    title = "Aussentemperatur taegliche und woechentliche MinMax-Temp"
    
    input1 = "outside_intermediate2.dat"
    intermediate_file = "outside_dailyWeekly_intermediate"
    output1 = "outside_daily.dat"
    output2 = "outside_weekly.dat"
    
    daily = 24*60*60
    weekly = 7*daily
    zero_time = 19*60*60 + 51*60 + 34
    offset = daily - zero_time
    np1 = np.loadtxt(input1)
    maxI = len(np1)
    start_time = np1[0][0] + offset # set to midnight
    
    if os.path.isfile("{}1.dat".format(intermediate_file)):
        print("Daily already written, if you want to reprocess rm {}".format("{}1.dat".format(intermediate_file)))
        np_daily = np.loadtxt("{}1.dat".format(intermediate_file))
    else:
        print("Step 1: write daily")
        time = start_time
        i=0
        dminmax = []
        while i < maxI:
            temps=[]
            try:
                while np1[i][0] < time + daily:
                    temp = np1[i][1]
                    temps.append(temp)
                    i=i+1
                midday = time +0.5*daily
                if temps:
                    tmin = min(temps)
                    tmax = max(temps)
                    dminmax.append([midday,tmin,tmax])
                time = time + daily
            except(IndexError):
                pass
        np_daily = np.array(dminmax)
        pP.write_array(np_daily, outputfilename="{}1.dat".format(intermediate_file))
    
    
    if os.path.isfile("{}2.dat".format(intermediate_file)):
        print("Weekly already written, if you want to reprocess rm {}".format("{}2.dat".format(intermediate_file)))
        np_weekly = np.loadtxt("{}2.dat".format(intermediate_file))
    else:
        print("Step 2: write weekly")
        time = start_time
        i=0
        dminmax = []
        while i < maxI:
            temps=[]
            try:
                while np1[i][0] < time + weekly:
                    temp = np1[i][1]
                    temps.append(temp)
                    i=i+1
                midweek = time +0.5*weekly
                if temps:
                    tmin = min(temps)
                    tmax = max(temps)
                    dminmax.append([midweek,tmin,tmax])
                time = time + weekly
            except(IndexError):
                pass
        np_weekly = np.array(dminmax)
        pP.write_array(np_weekly, outputfilename="{}2.dat".format(intermediate_file))
    
    
    if os.path.isfile("{}".format(output1)):
        print("Already finished processing daily to gnuplot readable file. If you want to re-process, rm {}".format(output1))
    else:    
        print("Step 3: re-write daily in rfc time, put double newline for measurement leaks, put header")
        with open(output1, "w") as out:
            out.write("# time    daily_min    daily_max  of air-temp_below_ceiling (processed with pp_room_minmax.py)\n")
            for row,content in enumerate(np_daily):
                try:
                    rfctime = pP._transform_float_to_rfc(content[0])
                    if np_daily[row][0] - np_daily[row-1][0] < 2*daily:
                        out.write("{}    {:f}    {:f}\n".format(rfctime,content[1],content[2]))
                    else:
                        out.write("\n\n{}    {:f}    {:f}\n".format(rfctime,content[1],content[2]))
                except(IndexError):
                    pass
                
    if os.path.isfile("{}".format(output2)):
        print("Already finished processing weekly to gnuplot readable file. If you want to re-process, rm {}".format(output2))
    else:    
        print("Step 4: re-write weekly in rfc time, put double newline for measurement leaks, put header")
        with open(output2, "w") as out:
            out.write("# time    weekly_min    weekly_max  of air-temp_below_ceiling (processed with pp_room_minmax.py)\n")
            for row,content in enumerate(np_weekly):
                try:
                    rfctime = pP._transform_float_to_rfc(content[0])
                    if np_weekly[row][0] - np_weekly[row-1][0] < 2*weekly:
                        out.write("{}    {:f}    {:f}\n".format(rfctime,content[1],content[2]))
                    else:
                        out.write("\n\n{}    {:f}    {:f}\n".format(rfctime,content[1],content[2]))
                except(IndexError):
                    pass
  
  
  
  
  
if __name__ == "__main__":
    main()
