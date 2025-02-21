# Astro App

Mostly this has backend functions related to astronomical calculations.

# AstroCalc View

This handles the "Calculators" page with a set of quick transformations:

1. **Distance from Modulus**: This convert a distance modulus (for galaxies, typically from HyperLeda) into Mly.
2. **Angular Size**: Given _d25_ and _r25_ values in log(0.1 arcmin) units (typically from HyperLeda), convert to "max x min" arcmin dimensions.
3. **SQS to SQM**:  Given surface/sky brightness in mag/arcsec^2 convert to mag/arcmin^2
4. **Bortle**: Estimate the Effective Bortle number (1-9) from sky SQM value (mag/arcmin^2)
5. **Time eQuinox**: convert an exposure time (mm:ss) to # of 4s frames recorded
6. **Time Seestar**: convert an exposure time (mm:ss) to a # of 10s frames recorded
7. **Frames eQuinox**: convert # of 4s frames to an exposure time (mm:ss)
8. **Frames Seestar**: convert # of 10s frames to an exposure time (mm:ss)