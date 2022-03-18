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

def main():
    title = "Wohnzimmer Raumtemperatur"
    pi_dir = "../../EARTHSHIP_Daten_vom_pi_selbst/human_readable_names/"
    
    input1 = "LivRoom_ceil.dat"
    input2 = "Kitchen_ceil_new.dat"
    input3 = os.path.join(pi_dir,input2)
    intermediate_file = "Wohnzimmer_temperatur_Luft_intermediate"
    output1 = "Wohnzimmer_temperatur_Luft.dat"
    
    pP = PostProcess()
    
    if os.path.isfile("{}3.dat".format(intermediate_file)):
        print("Files already converted to numpy-readable. If you want to re-process, rm {}".format("{}3.dat".format(intermediate_file)))
        np1 = np.loadtxt("{}1.dat".format(intermediate_file))
        np2 = np.loadtxt("{}2.dat".format(intermediate_file))
        np3 = np.loadtxt("{}3.dat".format(intermediate_file))
    else:
        print("Step 1-3: convert files to numpy readable format")
        np1 = pP.convert_to_np_array(input1)
        # sad but true: delete humidity from np1 (col 1) to be compatible with np2,np3
        np1 = np.delete(np1,(1),axis=1)
        np2 = pP.convert_to_np_array(input2)
        np3 = pP.convert_to_np_array(input3)
        pP.write_array(np1,outputfilename="{}1.dat".format(intermediate_file))
        pP.write_array(np2,outputfilename="{}2.dat".format(intermediate_file))
        pP.write_array(np3,outputfilename="{}3.dat".format(intermediate_file))

    
    if os.path.isfile("{}4.dat".format(intermediate_file)):
        print("Files already coarse filtered and kitchen concatenated. If you want to re-process, rm {}4.dat".format(intermediate_file))
        np23 = np.loadtxt("{}4.dat".format(intermediate_file))
    else:
        print("Step 4: coarse peak-filtering the files")
        np1 = pP.peak_filter_signal(np1,col=1,sample_len=30,rel_threshold=0.1,lower=11.0,upper=42.0)
        np2 = pP.peak_filter_signal(np2,col=1,sample_len=30,rel_threshold=0.1,lower=11.0,upper=42.0)
        np3 = pP.peak_filter_signal(np3,col=1,sample_len=30,rel_threshold=0.1,lower=11.0,upper=42.0)
        #merge numpy arrays:
        np23 = np.concatenate((np2,np3),axis=0)
        np23[np23[:,0].argsort()] # <-- strange thing but sorts according to 0th col
        # write integer time and temperature
        pP.write_array(np1,outputfilename="{}1.dat".format(intermediate_file))
        pP.write_array(np2,outputfilename="{}2.dat".format(intermediate_file))
        pP.write_array(np3,outputfilename="{}3.dat".format(intermediate_file))
        pP.write_array(np23,outputfilename="{}4.dat".format(intermediate_file))
        
        
    if os.path.isfile("{}5.dat".format(intermediate_file)):
        print("Kitchen already low passed. If you want to re-process, rm {}5.dat".format(intermediate_file))
        np23low = np.loadtxt("{}5.dat".format(intermediate_file))
    else:
        print("Step 5: low-pass filtering the kitchen")
        np23lin = pP.linear_resample_data(np23,dt=200.)
        np23low = pP.low_filter_lin_sampled_data(np23lin,cutoff_dt=12.*60.*60.)
        pP.write_array(np23low,outputfilename="{}5.dat".format(intermediate_file))
        
        
    if os.path.isfile("{}6.dat".format(intermediate_file)):
        print("Kitchen-low-pass already stripped of linear regions. If you want to re-process, rm {}6.dat".format(intermediate_file))
        np23strp = np.loadtxt("{}6.dat".format(intermediate_file))
    else:    
        print("Step 6: Stripping kitchen of points in measurement leaking times (now faster?)")
        dummy = []
        debug = []
        for row,content in enumerate(np23low):
            try:
                m = float(np23low[row][1] - np23low[row-1][1]) / float(np23low[row][0] - np23low[row-1][0])
                ytilde = m * (np23low[row+1][0] - np23low[row][0]) + np23low[row][1]
                diff = np.abs(ytilde - np23low[row+1][1])
                if diff > 1e-5:
                    dummy.append(content)
                else:
                    debug.append(content)
                    print("diff={}".format(diff))
            except(IndexError):
                #if row+2 exceeds index
                pass
            except(ZeroDivisionError):
                print(np23low[row-1])
                print(np23low[row])
                print("division by zero: m={}".format(m))
                exit(1)
        np23strp = np.array(dummy)
        deb = np.array(debug)
        pP.write_array(np23strp,outputfilename="{}6.dat".format(intermediate_file))
        pP.write_array(deb,outputfilename="debug.dat")
        
    if os.path.isfile("{}7.dat".format(intermediate_file)):
        print("Already concatenated living room and kitchen. If you want to re-process, rm {}7.dat".format(intermediate_file))
        np123 = np.loadtxt("{}7.dat".format(intermediate_file))
        overlap = np.loadtxt("Wohnzimmer_temperatur_Luft_overlap_Kueche_Wohnzimmer.dat")
        addon = np.loadtxt("Wohnzimmer_temperatur_Luft_addon_Kueche.dat")
    else:    
        print("Step 7: reduce low-passed kitchen in points and concatenate living room and stripped low-passed kitchen")
        reduced = np.array([content for row,content in enumerate(np23strp) if row%8 == 0])
        overlap = np.array([ i for i in reduced if i[0] < 1.51337e9])
        addon = np.array([ i for i in reduced if i[0] >= 1.51337e9])
        np123 = np.concatenate((np1,addon),axis=0)
        # sorting should not be needed...:
        #np123[np123[:,0].argsort()] # <-- strange thing but sorts according to 0th col
        pP.write_array(np123,outputfilename="{}7.dat".format(intermediate_file))
        pP.write_array(np123,outputfilename="Wohnzimmer_temperatur_Luft_raw.dat")
        pP.write_array(overlap,outputfilename="Wohnzimmer_temperatur_Luft_overlap_Kueche_Wohnzimmer.dat")
        pP.write_array(addon,outputfilename="Wohnzimmer_temperatur_Luft_addon_Kueche.dat")
        
    
    if os.path.isfile("{}".format(output1)):
        print("Already finished processing room-temp to gnuplot readable file. If you want to re-process, rm {}".format(output1))
    else:    
        print("Step 8: re-write in rfc time, put double newline for measurement leaks, put header")
        with open(output1, "w") as out:
            out.write("# time    air-temp_below_ceiling (already postprocessed with pp_room_temp.py)\n")
            for row,content in enumerate(np123):
                try:
                    rfctime = pP._transform_float_to_rfc(content[0])
                    if np123[row][0] - np123[row-1][0] < 3600.:
                        out.write("{}    {}\n".format(rfctime,content[1]))
                    else:
                        out.write("\n\n{}    {}\n".format(rfctime,content[1]))
                except(IndexError):
                    pass
            
        
  
if __name__ == "__main__":
    main()
