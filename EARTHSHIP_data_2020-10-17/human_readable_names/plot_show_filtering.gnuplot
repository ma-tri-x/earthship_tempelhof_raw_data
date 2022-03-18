#!/bin/gnuplot
reset
set term x11
set output
set encoding utf8

set key above

set grid
set xdata time
set title "Wohnzimmer und Küche Mai 2016\nLuft-Temperatur unter der Decke\nBeispiel zur Tiefpass-Filterung"
set ylabel "T [°C]"
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%d.%m.\n%H:%M"
plot "show_filtering_living_room.dat" u 1:2 w l lw 2 t "Wohnzimmer",\
     "show_filtering_kitchen_raw.dat" u 1:2 w l lw 2 t "Küche ungefiltert",\
     "show_filtering_kitchen_filtered.dat" u 1:2 w l lw 2 lc 8 t "Küche mit Tiefpassfilter"

# plot "show_filtering_intermediate1.dat" u 1:2 w l lw 2 t "Wohnzimmer",\
#      "show_filtering_intermediate2.dat" u 1:2 w l lw 2 t "Küche ungefiltert"
     
     #,\
     #"show_filtering_intermediate7.dat" u 1:2 w l lw 2 t "Küche mit Tiefpassfilter"

pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 16"
set output "Show_filtering.eps"
replot

!epstopdf Show_filtering.eps
!rm Show_filtering.eps
