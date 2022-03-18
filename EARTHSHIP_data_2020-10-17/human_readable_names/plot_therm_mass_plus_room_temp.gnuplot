#!/bin/gnuplot

reset
set term x11
set output
set encoding utf8

set key above
set grid
set xdata time
# set title "Temperatur in der Nordwand (ca. Mitte Wohnküche)\nund im Boden (Nordost-Ecke Wohnzimmer)\nim Vergleich zur wöchentlichen Raumtemperatur (unter der Decke)"
set ylabel "T [°C]"
set timefmt "%Y-%m-%dT%H:%M:%S.*Z"
set format x "%m\n20%y"

plot "Wohnzimmer_temperatur_Luft_weekly.dat" u 1:2 w l lw 2 lc 3 t "Raumtemp. min.", "" u 1:3 w l lw 2 lc 7 t "Raumtemp. max.",\
     "Therm_mass_simple_ground_floor_heating_pipes.dat" u 1:2  w l lw 2 lc 8 t "im Boden auf Höhe der Heizspiralen",\
     "Therm_mass_simple_north_wall.dat" u 1:2 w l lw 3 lc 2 t "147cm in der Nordwand"
     
pause -1

set term postscript eps color enhanced solid font "DejaVuSerif, 16"
set output "Therm_mass_simple_plus_room.eps"
replot

!epstopdf Therm_mass_simple_plus_room.eps
!rm Therm_mass_simple_plus_room.eps
