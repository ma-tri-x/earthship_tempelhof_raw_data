#!/bin/gnuplot
reset
set term x11
set output
set encoding utf8

set grid
set xdata time
set title "Wohnküche (tägliche Temperaturschwankung)\nLuft-Temperatur unter der Decke"
set ylabel "{/Symbol D}T [°C]"
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%m\n20%y"



plot "Wohnzimmer_temperatur_Luft_daily.dat" u 1:(abs(($3)-($2))) w l lw 2 t ""

pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 16"
set output "Wohnzimmer_daily_span.eps"
replot

!epstopdf Wohnzimmer_daily_span.eps
!rm Wohnzimmer_daily_span.eps
