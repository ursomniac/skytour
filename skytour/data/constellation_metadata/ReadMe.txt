File Summary:
--------------------------------------------------------------------------------
 FileName           Lrecl  Records   Explanations
--------------------------------------------------------------------------------
ReadMe                 80        .   This file
bound_ed.dat           23     1562   Boundary data from E. Delporte's book
verts_18.txt           38      694   Vertices (B1875, sex)
edges_18.txt           57      781   Edges (B1875, sex)
bound_verts_18.txt     38     1562   Boundary vertices (B1875, ccw, sex)
bound_edges_18.txt     57     1562   Boundary edges (B1875, ccw, sex)
bound_18.txt           23     1562   Boundaries (B1875, ccw, dec)
bound_in_18.txt        23    13238   Interpolated boundaries (B1875, ccw, dec)
bound_in_20.txt        23    13238   Interpolated boundaries (J2000, ccw, dec)
lines_18.txt           26     1194   Merged edges (B1875, dec)
lines_in_18.txt        26     7121   Interpolated merged edges (B1875, dec)
lines_in_20.txt        26     7121   Interpolated merged edges (J2000, dec)
centers_18.txt         32       89   Constellation centers (B1875, dec)
centers_20.txt         32       89   Constellation centers (J2000, dec)
--------------------------------------------------------------------------------

Byte-by-byte Description of file: bound_ed.dat
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1-  2  I2     h       RAh     Right ascension B1875 (hours)
       3  A1     ---     D1      [:] delimiter
   4-  5  I2     min     RAm     Right ascension B1875 (minutes)
       6  A1     ---     D2      [:] delimiter
   7-  8  I2     s       RAs     Right ascension B1875 (seconds)
      10  A1     ---     DE-     Declination B1875 (sign)
  11- 12  I2     deg     DEd     Declination B1875 (degrees)
      13  A1     ---     D3      [:] delimiter
  14- 15  I2     arcmin  DEm     Declination B1875 (minutes)
      16  A1     ---     D4      [:] delimiter
  17- 18  I2     arcsec  DEs     Declination B1875 (seconds)
  20- 23  A4     ---     Con     Constellation abbreviation
--------------------------------------------------------------------------------

Byte-by-byte Description of file: verts_18.txt and bound_verts_18.txt
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1-  3  A3     ---     Key     Vertex key
   5-  6  I2     h       RAh     Right ascension B1875 (hours)
       7  A1     ---     D1      [:] delimiter
   8-  9  I2     min     RAm     Right ascension B1875 (minutes)
      10  A1     ---     D2      [:] delimiter
  11- 12  I2     s       RAs     Right ascension B1875 (seconds)
      14  A1     ---     DE-     Declination B1875 (sign)
  15- 16  I2     deg     DEd     Declination B1875 (degrees)
      17  A1     ---     D3      [:] delimiter
  18- 19  I2     arcmin  DEm     Declination B1875 (minutes)
      20  A1     ---     D4      [:] delimiter
  21- 22  I2     arcsec  DEs     Declination B1875 (seconds)
  24- 38  A15    ---     Cons    Constellation abbreviations
--------------------------------------------------------------------------------

Byte-by-byte Description of file: edges_18.txt and bound_edges_18.txt
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1-  3  A3     ---     Key1    Key of 1st vertex
       4  A1     ---     D1      [:] delimiter
   5-  7  A3     ---     Key2    Key of 2nd vertex
       9  A1     ---     Type    Edge type: [M]eridian or [P]arallel
      10  A1     ---     Dir     Edge direction: + increasing or - decreasing
  12- 13  I2     h       RA1_h   Right ascension B1875 (hours) of 1st vertex
      14  A1     ---     D2      [:] delimiter
  15- 16  I2     min     RA1_m   Right ascension B1875 (minutes) of 1st vertex
      17  A1     ---     D3      [:] delimiter
  18- 19  I2     s       RA1_s   Right ascension B1875 (seconds) of 1st vertex
      21  A1     ---     DE1-    Declination B1875 (sign) of 1st vertex
  22- 23  I2     deg     DE1_d   Declination B1875 (degrees) of 1st vertex
      24  A1     ---     D4      [:] delimiter
  25- 26  I2     arcmin  DE1_m   Declination B1875 (minutes) of 1st vertex
      27  A1     ---     D5      [:] delimiter
  28- 29  I2     arcsec  DE1_s   Declination B1875 (seconds) of 1st vertex
  31- 32  I2     h       RA2_h   Right ascension B1875 (hours) of 2nd vertex
      33  A1     ---     D6      [:] delimiter
  34- 35  I2     min     RA2_m   Right ascension B1875 (minutes) of 2nd vertex
      36  A1     ---     D7      [:] delimiter
  37- 38  I2     s       RA2_s   Right ascension B1875 (seconds) of 2nd vertex
      40  A1     ---     DE2-    Declination B1875 (sign) of 2nd vertex
  41- 42  I2     deg     DE2_d   Declination B1875 (degrees) of 2nd vertex
      43  A1     ---     D8      [:] delimiter
  44- 45  I2     arcmin  DE2_m   Declination B1875 (minutes) of 2nd vertex
      46  A1     ---     D9      [:] delimiter
  47- 48  I2     arcsec  DE2_s   Declination B1875 (seconds) of 2nd vertex
  50- 57  A8     ---     Cons    Constellation abbreviations
--------------------------------------------------------------------------------

Byte-by-byte Description of file: bound_18.txt and bound_in_18.txt
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1- 10  F10.7  h       RAhr    Right ascension B1875 (decimal hours)
      12  A1     ---     DE-     Declination B1875 (sign)
  13- 21  F9.6   deg     DEdeg   Declination B1875 (decimal degrees)
  23- 26  A4     ---     Con     Constellation abbreviation
--------------------------------------------------------------------------------

Byte-by-byte Description of file: bound_in_20.txt
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1- 10  F10.7  h       RAhr    Right ascension J2000 (decimal hours)
      12  A1     ---     DE-     Declination J2000 (sign)
  13- 21  F9.6   deg     DEdeg   Declination J2000 (decimal degrees)
  23- 26  A4     ---     Con     Constellation abbreviation
--------------------------------------------------------------------------------

Byte-by-byte Description of file: lines_18.txt and lines_in_18.txt
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1- 10  F10.7  h       RAhr    Right ascension B1875 (decimal hours)
      12  A1     ---     DE-     Declination B1875 (sign)
  13- 21  F9.6   deg     DEdeg   Declination B1875 (decimal degrees)
  23- 29  A7     ---     Key     Segment key
--------------------------------------------------------------------------------

Byte-by-byte Description of file: lines_in_20.txt
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1- 10  F10.7  h       RAhr    Right ascension J2000 (decimal hours)
      12  A1     ---     DE-     Declination J2000 (sign)
  13- 21  F9.6   deg     DEdeg   Declination J2000 (decimal degrees)
  23- 29  A7     ---     Key     Segment key
--------------------------------------------------------------------------------

Byte-by-byte Description of file: centers_18.txt
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1- 10  F10.7  h       RAhr    Right ascension B1875 (decimal hours) of center
      12  A1     ---     DE-     Declination B1875 (sign) of center
  13- 21  F9.6   deg     DEdeg   Declination B1875 (decimal degrees) of center
  23- 29  F7.2   deg2    Area    Constellation area (square degrees)
  31- 32  I2     ---     Rank    Constellation rank in area
  34- 37  A4     ---     Con     Constellation abbreviation
--------------------------------------------------------------------------------

Byte-by-byte Description of file: centers_20.txt
--------------------------------------------------------------------------------
   Bytes  Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1- 10  F10.7  h       RAhr    Right ascension J2000 (decimal hours) of center
      12  A1     ---     DE-     Declination J2000 (sign) of center
  13- 21  F9.6   deg     DEdeg   Declination J2000 (decimal degrees) of center
  23- 29  F7.2   deg2    Area    Constellation area (square degrees)
  31- 32  I2     ---     Rank    Constellation rank in area
  34- 37  A4     ---     Con     Constellation abbreviation
--------------------------------------------------------------------------------

History:

  * 2018-03-01: increased the precision of right ascensions from F8.5 to F10.7
    and of declinations from F8.5 to F9.6 in centers_18.txt, centers_20.txt,
    bound_18.txt, lines_18.txt, bound_in_18.txt, lines_in_18.txt,
    bound_in_20.txt, and lines_in_20.txt.
  * 2022-04-06: consistently spell "Byte-by-byte Description of file" rather
    than "... files".

================================================================================
