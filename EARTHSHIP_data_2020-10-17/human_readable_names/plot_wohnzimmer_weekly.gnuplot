#!/bin/gnuplot
reset
set term x11
set output
set encoding utf8

set grid
set xdata time
set title "Wohnküche (wöchentliches Minimum und Maximum)\nLuft-Temperatur unter der Decke"
set ylabel "T [^oC]"
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%m\n20%y"
plot "Wohnzimmer_temperatur_Luft_weekly.dat" u 1:2 w l lw 2 lc 3 t "min.", "" u 1:3 w l lw 2 lc 7 t "max."

pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 16"
set output "Wohnzimmer_weekly.eps"
replot

!epstopdf Wohnzimmer_weekly.eps
!rm Wohnzimmer_weekly.eps
