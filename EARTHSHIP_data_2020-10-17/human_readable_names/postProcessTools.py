import os, json
import sys, glob
from datetime import datetime as dt
import time
import numpy as np
from scipy.signal import butter, lfilter, freqz, filtfilt
import matplotlib.pyplot as plt

class PostProcess(object):
    def __init__(self):
        #,translation_dict="Zuordnung.json",outputfilename="output.dat"):
        #self.translation_dict = json.load(open(translation_dict,"r"))
        #self.outputfilename = outputfilename
        print("instantiating a funny postprocess class")

    def _butter_lowpass(self,cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def _butter_lowpass_filter(self,data, cutoff, fs, order=5):
        b, a = _butter_lowpass(cutoff, fs, order=order)
        #y = lfilter(b, a, data)
        y = filtfilt(b, a, data)
        return y

    def _linear_resample(self,np_array_read,col, dt_want):
        t = np_array_read[0][0]
        index = 1
        resampled_list = []
        while index < len(np_array_read):
            while t < np_array_read[index][0]:
                t+=dt_want
                #print t
                resampled_list.append((np_array_read[index][col]-np_array_read[index-1][col])/
                                    (np_array_read[index][0]  -np_array_read[index-1][0])*(t-np_array_read[index-1][0])
                                    +np_array_read[index-1][col])
            index+=1
        return np.array(resampled_list)

    def linear_resample_data(self,inputarray,dt=200.):
        a = inputarray.copy() #kitchen_part.dat")
        T = a[-1][0]-a[0][0]
        n = int(T/dt)+1
        t = np.linspace(a[0][0], a[-1][0], n, endpoint=True)
        b = self._linear_resample(a,1,dt)
        new_data = np.array([t,b]).T
        #print new_data
        return new_data

    def _butter_lowpass_coeffs(self,cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a
    
    def _butter_lowpass_filtfilter(self,data, cutoff, fs, order=5):
        # Get the filter coefficients so we can check its frequency response.
        b, a = self._butter_lowpass_coeffs(cutoff, fs, order=order)
        #y = lfilter(b, a, data)
        y = filtfilt(b, a, data)
        return y

    def low_filter_lin_sampled_data(self,lin_samp_data,cutoff_dt=2.*60.*60.):
        dt = lin_samp_data[1][0]-lin_samp_data[0][0]
        wanted_samplerate = 1./dt
        min_dt = cutoff_dt # 2 hours cutoff

        # Filter requirements.
        order = 6
        fs = wanted_samplerate       # sample rate, Hz
        cutoff = 1./min_dt  # desired cutoff frequency of the filter, Hz

        t = lin_samp_data.T[0]
        b = lin_samp_data.T[1]

        # Filter the data
        y = self._butter_lowpass_filtfilter(b, cutoff, fs, order)
        new_data = np.array([t,y]).T 
        return new_data


    def clip_temp(self,inputfile,lower=0.0,upper=50.0):
        with open('{}'.format(inputfile),'r') as infile:
            lines = infile.readlines()
        newlines = []
        for k in lines[1:]:
            cols = k.split("    ")
            cols.pop()
            T=len(cols)
            try:
                float(cols[T-1])
                if float(cols[T-1]) < upper and float(cols[T-1]) > lower:
                    newlines.append(k)
                else:
                    print "skip line with T={}".format(cols[T-1])
            except(ValueError):
                pass
        return newlines
    
    def convert_to_np_array(self,inputfile):
        l = []
        print("converting {} data to a numpy array".format(inputfile))
        with open(inputfile,'r') as inf:
            lines = inf.readlines()
        firstline = lines[1].split("    ")
        firstline.pop()
        col_len = len(firstline)-firstline.count("None")
        for line in lines[1:]:
            line.replace("\n","")
            cols = line.split("    ")
            if ("None" in cols[1:]) or ("1" in cols[1:]):
                pass
            entry = []
            entry.append( self.datetime_to_float( self.rfctime_to_datetime(cols[0])) )
            for col in cols[1:]: 
                try:
                    entry.append(float(col)) 
                except(ValueError):
                    pass
            if len(entry) == col_len: l.append(entry)
        return np.array(l)
      
    def peak_filter_signal(self,inputarray,col,sample_len,rel_threshold,lower=0.0,upper=50.0,debug=False):
        ## conversion to numpy array
        if not type(inputarray) is np.ndarray:
            print("input must be of np.array type")
            exit(1)
        tT = inputarray.copy()
        ## peak filtering:
        print "peak filtering data ..."
        index = 0
        while index < len(tT.T[0]):
            avgT = np.average(tT.T[col][index:index+sample_len])
            del_items = []
            for j,T in enumerate(tT.T[col][index:index+sample_len]):
                if np.abs(T-avgT)/np.abs(avgT) > rel_threshold or T < lower or T>upper:
                    if debug: print "popping: ", j, T, tT[index+j][col]
                    del_items.append(j)
            tT = np.delete(tT,np.array(del_items)+index,axis=0)
            index += sample_len - len(del_items)
        return tT
        
    def make_rfc_data(self,inputarray):
        print "converting data back to rfc time..."
        tT = inputarray.copy()
        tTT = tT.T.copy()
        newlines = []
        index = 0
        while index < len(tTT[0]):
            t = self._transform_float_to_rfc(tT[index][0])
            cols = "{}".format(t)
            for item in tT[index][1:]:
                cols = cols + "    {}".format(item)
            newlines.append(cols)
            index +=1
        return newlines
                
    def _transform_float_to_rfc(self,dt_num):
        return (dt.fromtimestamp(float(dt_num))).strftime(format="%Y-%m-%dT%H:%M:%SZ")
    
    def _transform_float_to_datetime(self,dt_num):
        return (dt.fromtimestamp(float(dt_num)))
    
    def make_string_from_float_list(self,array_1d):
        s = ""
        for i in array_1d:
            s = "{}    {}".format(s,i)
        return s
            
    
    def write_outputfile(self,array, outputfilename=""):
        if not outputfilename: outputfilename = self.outputfilename
        lines = self.make_rfc_data(array)
        with open(outputfilename,"w") as outfile:
            for line in lines:
                outfile.write(line + "\n")
                
    def write_array(self,array, outputfilename="out_array.dat"):
        np.savetxt(outputfilename, array, delimiter="    ", fmt="%f")

    def write_gnuplot_file(self,gnuplot_col=2,title="some_title",ylabel="T [^oC]"):
        with open('{}.gnuplot'.format((self.outputfilename).split(".")[0]),'w') as g:
            g.write('reset\n\
                set term postscript eps color enhanced solid\n\
                set output \"{}.eps\"\n\
                set xdata time\n\
                set grid\n\
                set title \"{}\"\n\
                set ylabel \"{}\"\n\
                set timefmt "%Y-%m-%dT%H:%M:%S.*Z"\n\
                set format x "%y/%m"\n\
                plot \"{}\" u 1:{} w l t \"\"'.format((self.outputfilename).split(".")[0],title,ylabel,self.outputfilename,gnuplot_col)
                )
            
    def rfctime_to_datetime(self,rfctime):
        stripped_rfctime = rfctime[:19]
        #print stripped_rfctime
        return dt.strptime(stripped_rfctime,"%Y-%m-%dT%H:%M:%S")

    def datetime_to_float(self,dtobj):
        #epoch = dt.utcfromtimestamp(0) #da der timestamp schon utc ist, braucht es das nicht mehr
        epoch = dt.fromtimestamp(3600) #=0, aber muss weil dann ein timedelta obj entsteht
        return (dtobj - epoch).total_seconds()
    
