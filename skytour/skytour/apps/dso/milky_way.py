"""
from http://pp3.sourceforge.net/manual/Milky-Way-data-file.html


B.5 Milky Way data file
This is a text file usually called milkyway.dat.

Its header is extremely simple: It consists of only one number which 
is the maximal (= equatorial) diagonal half distance of two pixels in degrees. 
This value is used as the radius for the milky way pixels. Of course it must be 
the minimal radius for which there are no gaps between the pixels.

What follows are the Milky Way pixels themselves. Each consists of tree entries, 
separated by white space:

* the rectascension in hours,
* the declination in degrees, and
* the grey value of the pixel from 1 to 255. 

Zero is not used because zero-value pixels are not included into the data file anyway.

Example
     0.212
     11.885 0.259 1
     11.962 0.295 5
     11.974 0.298 5
     
     17.982 -26.999 136
     17.982 -27.299 158
     17.982 -27.599 169
     17.982 -27.899 199
     17.981 -28.199 235

PP3's boundary data origin
I used the All-Sky Milky Way Panorama by Axel Mellinger. 
His bitmap with the two hemispheres in equidistant azimuthal projection was greyscaled 
and smoothed with the Gimp, and then transformed to PP3's format with a small hand-written C program.
"""