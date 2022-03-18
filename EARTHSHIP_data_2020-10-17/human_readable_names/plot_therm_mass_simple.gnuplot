#!/bin/gnuplot

reset
set term x11
set output
set encoding utf8

set key above
set grid
set xdata time
# set title "Temperatur in der Nordwand (ca. Mitte Wohnküche)\nund im Boden (Nordost-Ecke Wohnzimmer)"
set ylabel "T [^oC]"
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%m\n20%y"

plot "Therm_mass_simple_north_wall.dat" u 1:2 w l lw 2 lc 2 t "147cm in der Nordwand",\
     "Therm_mass_simple_ground_floor_20cm.dat" u 1:2  w l t "ca. 20cm im Boden",\
     "Therm_mass_simple_ground_floor_heating_pipes.dat" u 1:2  w l lc 8 t "im Boden auf Höhe der Heizspiralen"
     
pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 18"
set output "Therm_mass_simple.eps"
replot

!epstopdf Therm_mass_simple.eps
!rm Therm_mass_simple.eps
