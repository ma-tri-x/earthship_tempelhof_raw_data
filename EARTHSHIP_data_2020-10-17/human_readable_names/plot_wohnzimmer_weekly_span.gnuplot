#!/bin/gnuplot
reset
set term x11
set output
set encoding utf8

set grid
set xdata time
set title "Wohnküche (wöchentliche Minima und Maxima der \ntäglichen Temperaturschwankung)\nLuft-Temperatur unter der Decke"
set ylabel "{/Symbol D}T [°C]"
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%m\n20%y"



plot "Wohnzimmer_daily_span_weekly_minavgmax.dat" u 1:2 w l lw 2 t "min.",\
     "Wohnzimmer_daily_span_weekly_minavgmax.dat" u 1:4 w l lw 2 t "max."

pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 16"
set output "Wohnzimmer_weekly_span.eps"
replot

!epstopdf Wohnzimmer_weekly_span.eps
!rm Wohnzimmer_weekly_span.eps
