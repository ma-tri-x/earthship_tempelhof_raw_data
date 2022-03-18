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
    title = "Thermische Masse (einfach)"
    pi_dir = "../../EARTHSHIP_Daten_vom_pi_selbst/human_readable_names/"
    
    input1 = "NorthWall_147cm_depth.dat"
    input2 = "ground_floor_appr_20cm_below_feet.dat"
    input3 = "ground_floor_slightly_above_heating_pipes.dat"
    ## Pi not needed. Same data:
    #input2p = os.path.join(pi_dir,input2) 
    #input3p = os.path.join(pi_dir,input3)
    intermediate_file = "Therm_mass_intermediate"
    output1 = "Therm_mass_simple_north_wall.dat"
    output2 = "Therm_mass_simple_ground_floor_20cm.dat"
    output3 = "Therm_mass_simple_ground_floor_heating_pipes.dat"
    
    
    if os.path.isfile("{}3.dat".format(intermediate_file)):
        print("Files already converted to numpy-readable. If you want to re-process, rm {}".format("{}3.dat".format(intermediate_file)))
        np1 = np.loadtxt("{}1.dat".format(intermediate_file))
        np2 = np.loadtxt("{}2.dat".format(intermediate_file))
        np3 = np.loadtxt("{}3.dat".format(intermediate_file))
    else:
        print("Step 1-3: convert files to numpy readable format")
        np1 = pP.convert_to_np_array(input1)
        np2 = pP.convert_to_np_array(input2)
        np3 = pP.convert_to_np_array(input3)
        pP.write_array(np1,outputfilename="{}1.dat".format(intermediate_file))
        pP.write_array(np2,outputfilename="{}2.dat".format(intermediate_file))
        pP.write_array(np3,outputfilename="{}3.dat".format(intermediate_file))

    
    if os.path.isfile("{}6.dat".format(intermediate_file)):
        print("Files already coarse filtered. If you want to re-process, rm {}6.dat".format(intermediate_file))
        np4 = np.loadtxt("{}4.dat".format(intermediate_file))
        np5 = np.loadtxt("{}5.dat".format(intermediate_file))
        np6 = np.loadtxt("{}6.dat".format(intermediate_file))
    else:
        print("Step 4-6: coarse peak-filtering the files")
        np4 = pP.peak_filter_signal(np1,col=1,sample_len=30,rel_threshold=0.1,lower=10.0,upper=25.0)
        np5 = pP.peak_filter_signal(np2,col=1,sample_len=30,rel_threshold=0.1,lower=10.0,upper=25.0)
        np6 = pP.peak_filter_signal(np3,col=1,sample_len=30,rel_threshold=0.1,lower=10.0,upper=25.0)
        # write integer time and temperature
        pP.write_array(np4,outputfilename="{}4.dat".format(intermediate_file))
        pP.write_array(np5,outputfilename="{}5.dat".format(intermediate_file))
        pP.write_array(np6,outputfilename="{}6.dat".format(intermediate_file))
    
        
        
    if os.path.isfile("{}7.dat".format(intermediate_file)):
        print("Therm mass already cut off before break. If you want to re-process, rm {}7.dat".format(intermediate_file))
        np7 = np.loadtxt("{}7.dat".format(intermediate_file))
    else:
        print("Step 7: cutoff therm mass before 1.48947e9")
        np7 = np.array([ x for x in np4 if x[0] < 1.48947e9])
        pP.write_array(np7,outputfilename="{}7.dat".format(intermediate_file))
        
        
    if os.path.isfile("{}".format(output3)):
        print("Already finished processing therm masses to gnuplot readable files. If you want to re-process, rm {}".format(output3))
    else:    
        print("Step 8: re-write in rfc time, put double newline for measurement leaks, put header")
        make_rfc_gnuplot_readable_file(output1, "# time    temp_in_north_wall_147cm (already processed with pp_therm_mass_simple.py)", np7)
        make_rfc_gnuplot_readable_file(output2, "# time    temp_in_ground_floor_20cm (already processed with pp_therm_mass_simple.py)", np5)
        make_rfc_gnuplot_readable_file(output3, "# time    temp_in_ground_floor_above_heating_pipes (already processed with pp_therm_mass_simple.py)", np6)
        
  
if __name__ == "__main__":
    main()
