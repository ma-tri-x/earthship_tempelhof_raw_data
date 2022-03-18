#!/bin/gnuplot
reset
set term x11
set output
set encoding utf8

set grid
set xdata time
set title "Wohnzimmer und Küche\nLuft-Temperatur unter der Decke"
set ylabel "T [^oC]"
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%m\n20%y"
plot "Wohnzimmer_temperatur_Luft.dat" u 1:2 w l lw 2 t ""

pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 16"
set output "Wohnzimmer.eps"
replot

!epstopdf Wohnzimmer.eps
!rm Wohnzimmer.eps
