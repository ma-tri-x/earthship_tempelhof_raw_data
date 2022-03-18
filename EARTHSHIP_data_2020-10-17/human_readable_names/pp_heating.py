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
    title = "Heizung"
    #pi_dir = "../../EARTHSHIP_Daten_vom_pi_selbst/human_readable_names/"
    
    input1 = "heating_backflow.dat"
    input2 = "heating_inflow.dat"
    intermediate_file = "heating_intermediate"
    output1 = "heating_backflow_finish.dat"
    output2 = "heating_inflow_finish.dat"
    
    if os.path.isfile("{}2.dat".format(intermediate_file)):
        print("Files already converted to numpy-readable. If you want to re-process, rm {}".format("{}2.dat".format(intermediate_file)))
        np1 = np.loadtxt("{}1.dat".format(intermediate_file))
        np2 = np.loadtxt("{}2.dat".format(intermediate_file))
    else:
        print("Step 1-2: convert files to numpy readable format")
        np1 = pP.convert_to_np_array(input1)
        np2 = pP.convert_to_np_array(input2)
        pP.write_array(np1,outputfilename="{}1.dat".format(intermediate_file))
        pP.write_array(np2,outputfilename="{}2.dat".format(intermediate_file))

    
    if os.path.isfile("{}4.dat".format(intermediate_file)):
        print("Files already coarse filtered. If you want to re-process, rm {}4.dat".format(intermediate_file))
        np3 = np.loadtxt("{}3.dat".format(intermediate_file))
        np4 = np.loadtxt("{}4.dat".format(intermediate_file))
    else:
        print("Step 3-4: coarse peak-filtering the files")
        np3 = pP.peak_filter_signal(np1,col=1,sample_len=30,rel_threshold=0.1,lower=8.0,upper=60.0)
        np4 = pP.peak_filter_signal(np2,col=1,sample_len=30,rel_threshold=0.1,lower=8.0,upper=60.0)
        # write integer time and temperature
        pP.write_array(np3,outputfilename="{}3.dat".format(intermediate_file))
        pP.write_array(np4,outputfilename="{}4.dat".format(intermediate_file))
        
        
    if os.path.isfile("{}".format(output2)):
        print("Already finished processing files to gnuplot readable file. If you want to re-process, rm {}".format(output2))
    else:    
        print("Step 5: re-write in rfc time, put double newline for measurement leaks, put header")
        make_rfc_gnuplot_readable_file(output1, "# time    temp_heating_backflow (processed by pp_heating.py)", np3)
        make_rfc_gnuplot_readable_file(output2, "# time    temp_heating_inflow (processed by pp_heating.py)", np4)
            
        
  
if __name__ == "__main__":
    main()
