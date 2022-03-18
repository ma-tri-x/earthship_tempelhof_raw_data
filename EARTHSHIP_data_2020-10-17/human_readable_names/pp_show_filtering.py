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
    title = "Kueche Temperatur Vergleich Filterung und Rohdaten"
    #pi_dir = "../../EARTHSHIP_Daten_vom_pi_selbst/human_readable_names/"
    
    input1 = "LivRoom_ceil.dat"
    input2 = "Kitchen_ceil_new.dat"
    intermediate_file = "show_filtering_intermediate"
    output1 = "show_filtering_living_room.dat"
    output2 = "show_filtering_kitchen_raw.dat"
    output3 = "show_filtering_kitchen_filtered.dat"
    
    start_cut = pP.datetime_to_float( pP.rfctime_to_datetime("2016-05-01T00:00:00.00000000Z") )
    end_cut = pP.datetime_to_float( pP.rfctime_to_datetime("2016-05-31T00:00:00.00000000Z") )
    
    if os.path.isfile("{}2.dat".format(intermediate_file)):
        print("Files already converted to numpy-readable and cut off for Mai 2016. If you want to re-process, rm {}".format("{}2.dat".format(intermediate_file)))
        np1 = np.loadtxt("{}1.dat".format(intermediate_file))
        np2 = np.loadtxt("{}2.dat".format(intermediate_file))
    else:
        print("Step 1-2: convert files to numpy readable format")
        np1 = pP.convert_to_np_array(input1)
        # sad but true: delete humidity from np1 (col 1)
        np1 = np.delete(np1,(1),axis=1)
        np2 = pP.convert_to_np_array(input2)
        # shorten to Mai 2016
        np1 = np.array([ x for x in np1 if x[0] < end_cut and x[0] > start_cut])
        np2 = np.array([ x for x in np2 if x[0] < end_cut and x[0] > start_cut])
        pP.write_array(np1,outputfilename="{}1.dat".format(intermediate_file))
        pP.write_array(np2,outputfilename="{}2.dat".format(intermediate_file))

    
    if os.path.isfile("{}4.dat".format(intermediate_file)):
        print("Files already coarse filtered. If you want to re-process, rm {}4.dat".format(intermediate_file))
        np3 = np.loadtxt("{}3.dat".format(intermediate_file))
        np4 = np.loadtxt("{}4.dat".format(intermediate_file))
    else:
        print("Step 3-4: coarse peak-filtering the files")
        np3 = pP.peak_filter_signal(np1,col=1,sample_len=30,rel_threshold=0.1,lower=11.0,upper=42.0)
        np4 = pP.peak_filter_signal(np2,col=1,sample_len=30,rel_threshold=0.1,lower=11.0,upper=42.0)
        # write integer time and temperature
        pP.write_array(np3,outputfilename="{}3.dat".format(intermediate_file))
        pP.write_array(np4,outputfilename="{}4.dat".format(intermediate_file))
        
        
    if os.path.isfile("{}5.dat".format(intermediate_file)):
        print("Kitchen already low passed. If you want to re-process, rm {}5.dat".format(intermediate_file))
        np5 = np.loadtxt("{}5.dat".format(intermediate_file))
    else:
        print("Step 5: low-pass filtering the kitchen")
        np5lin = pP.linear_resample_data(np4,dt=200.)
        np5low = pP.low_filter_lin_sampled_data(np5lin,cutoff_dt=12.*60.*60.)
        pP.write_array(np5low,outputfilename="{}5.dat".format(intermediate_file))
        
        
    if os.path.isfile("{}6.dat".format(intermediate_file)):
        print("Kitchen-low-pass already stripped of linear regions. If you want to re-process, rm {}6.dat".format(intermediate_file))
        np6 = np.loadtxt("{}6.dat".format(intermediate_file))
    else:    
        print("Step 6: Stripping kitchen of points in measurement leaking times (now faster?)")
        dummy = []
        debug = []
        for row,content in enumerate(np5low):
            try:
                m = float(np5low[row][1] - np5low[row-1][1]) / float(np5low[row][0] - np5low[row-1][0])
                ytilde = m * (np5low[row+1][0] - np5low[row][0]) + np5low[row][1]
                diff = np.abs(ytilde - np5low[row+1][1])
                if diff > 1e-5:
                    dummy.append(content)
                else:
                    debug.append(content)
                    #print("diff={}".format(diff))
            except(IndexError):
                #if row+2 exceeds index
                pass
            except(ZeroDivisionError):
                print(np5low[row-1])
                print(np5low[row])
                print("division by zero: m={}".format(m))
                exit(1)
        np6 = np.array(dummy)
        pP.write_array(np6,outputfilename="{}6.dat".format(intermediate_file))
        
    if os.path.isfile("{}7.dat".format(intermediate_file)):
        print("Already reduced low-passed kitchen to every 8th point. If you want to re-process, rm {}7.dat".format(intermediate_file))
        np7 = np.loadtxt("{}7.dat".format(intermediate_file))
    else:    
        print("Step 7: reduce low-passed kitchen in points")
        np7 = np.array([content for row,content in enumerate(np6) if row%8 == 0])
        pP.write_array(np7,outputfilename="{}7.dat".format(intermediate_file))

    
    if os.path.isfile("{}".format(output3)):
        print("Already finished processing files to gnuplot readable file. If you want to re-process, rm {}".format(output3))
    else:    
        print("Step 8: re-write in rfc time, put double newline for measurement leaks, put header")
        make_rfc_gnuplot_readable_file(output1, "# time    temp_living_room_Mai_2016 (processed by pp_show_filtering.py)", np3)
        make_rfc_gnuplot_readable_file(output2, "# time    temp_kitchen_old_raw_Mai_2016 (processed by pp_show_filtering.py)", np4)
        make_rfc_gnuplot_readable_file(output3, "# time    temp_kitchen_old_filtered_Mai_2016 (processed by pp_show_filtering.py)", np7)
            
        
  
if __name__ == "__main__":
    main()
