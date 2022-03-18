#!/bin/gnuplot

reset
set term x11
set output
set encoding utf8

set key above
set grid
set xdata time
set title "Heizungvor- und Rücklauftemperatur"
set ylabel "T [°C]"
# set y2label "T [°C] Außentemperatur"
# set y2tics
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%m\n20%y"

plot "heating_inflow_finish.dat" u 1:2  w l lc 7 t "Heizung Vorlauf",\
   "heating_backflow_finish.dat" u 1:2  w l lc 3 t "Heizung Rücklauf"
   
   #,\
   #"outside_weekly.dat" u 1:2 w l lc 1 axes x1y2 t "Außen-Temperatur min.",\
   #""                   u 1:3 w l lc 2 axes x1y2 t "Außen-Temperatur max."
     
# pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 18"
set output "heating.eps"
replot

!epstopdf heating.eps
!rm heating.eps
