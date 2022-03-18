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
    
    input1 = "Outside.dat"
    intermediate_file = "outside_intermediate"
    output1 = "outside_finish.dat"
    
    if os.path.isfile("{}1.dat".format(intermediate_file)):
        print("File already converted to numpy-readable. If you want to re-process, rm {}".format("{}1.dat".format(intermediate_file)))
        np1 = np.loadtxt("{}1.dat".format(intermediate_file))
    else:
        print("Step 1: convert file to numpy readable format")
        np1 = pP.convert_to_np_array(input1)
        # sad but true: delete humidity from np1 (col 1)
        np1 = np.delete(np1,(1),axis=1)
        pP.write_array(np1,outputfilename="{}1.dat".format(intermediate_file))
        
    
    if os.path.isfile("{}2.dat".format(intermediate_file)):
        print("Files already coarse filtered. If you want to re-process, rm {}2.dat".format(intermediate_file))
        np2 = np.loadtxt("{}2.dat".format(intermediate_file))
    else:
        print("Step 2: coarse peak-filtering the files")
        np2 = pP.peak_filter_signal(np1,col=1,sample_len=30,rel_threshold=0.1,lower=-20.0,upper=42.0)
        # write integer time and temperature
        pP.write_array(np2,outputfilename="{}2.dat".format(intermediate_file))
        
        
    if os.path.isfile("{}".format(output1)):
        print("Already finished processing file to gnuplot readable file. If you want to re-process, rm {}".format(output1))
    else:    
        print("Step 3: re-write in rfc time, put double newline for measurement leaks, put header")
        make_rfc_gnuplot_readable_file(output1, "# time    temp_outside (processed by pp_outside.py)", np2)
            
        
  
if __name__ == "__main__":
    main()
