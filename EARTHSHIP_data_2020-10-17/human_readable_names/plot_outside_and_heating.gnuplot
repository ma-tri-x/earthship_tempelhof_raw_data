#!/bin/gnuplot

reset
set term x11
set output
set encoding utf8

set key above
set grid
set xdata time
set title "Außen-Temperatur (wöchentliche Min./Max.)\nund Heizungvorlauftemperatur"
set ylabel "T [°C]"
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%m\n20%y"

plot "outside_weekly.dat" u 1:2 w l lc 3 t "Außen-Temperatur min.",\
     ""                   u 1:3 w l lc 4 t "Außen-Temperatur max.",\
     "heating_inflow_finish.dat" u 1:2  w l lc 7 t "Heizung Vorlauf"
     
pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 18"
set output "Outside_and_heating.eps"
replot

!epstopdf Outside_and_heating.eps
!rm Outside_and_heating.eps
