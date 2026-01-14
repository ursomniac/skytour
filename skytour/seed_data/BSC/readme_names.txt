
....Edit 10 rows of file 'index.dat.gz' with form=a
#!form=a
${FK5} ${RAh} ${RAm} ${RAs} ${pmRA} ${DE-}${DEd} ${DEm} ${DEs} ${pmDE} ${EpRA-1900} ${EpDE-1900} ${Vmag} ${Sp} ${DM} ${SAO} ${HD} ${BFno} ${name}
 (hit Return)
## (from tabmap V6.0 (2016-08-18)) 2022-01-16T20:48:21
#---------------------------------------------------------------------------
#-- IV/22 FK5 - SAO - HD - Common Name Cross Index (Smith 1996)
#--------------------------------------------------------------------------
#---Table: IV/22/index.dat.gz The catalog  (1535 records)
#Equinox=J2000
#-------------------------------------------------------------------------------
#     Label Format Unit     Explanations
#-------------------------------------------------------------------------------
#       FK5 I4     ---      The FK5 number (Cat. I/149, I/175) (2)
#       RAh I2     h        Right Ascension hours (J2000)
#       RAm I2     min      Right Ascension minutes (J2000)
#       RAs F6.3   s        Right Ascension seconds (J2000)
#      pmRA F7.3   10ms/yr  Proper motion in right ascension
#       DE- A1     ---      Declination sign
#       DEd I2     deg      Declination degrees (J2000)
#       DEm I2     arcmin   Declination minutes (J2000)
#       DEs F5.2   arcsec   Declination seconds (J2000)
#      pmDE F7.2   10mas/yr Proper motion in declination
# EpRA-1900 F5.2   yr       Epoch for right ascension -1900
# EpDE-1900 F5.2   yr       Epoch for declination -1900
#      Vmag F5.2   mag      Visual magnitude
#        Sp A2     ---      Spectral type
#        DM A10    ---      Durchmusterung Identification (1)
#       SAO I6     ---      ? SAO number (Cat. I/131)
#        HD I6     ---      ? HD number (Cat. III/135)
#      BFno A9     ---      Bayer or Flamsteed number
#      name A20    ---      Common name or variable name
#-------------------------------------------------------------------------------
#Note (1): this identification groups the Bonner Durchmusterung
#    (BD, Cat. I/122), the Sudlicher Durchmusterung (SD, Cat. I/119);
#    the Cordoba Durchmusterung (CD, Cat. I/114); and the
#    Cape Photographic Durchmusterung (CP, Cat. I/108).
#    The Durchmusterung is coded in bytes 69-70, the zone in bytes
#    71-73, the number in the zone in bytes 74-78
#Note (2):
#   The author has tabulated the following FK5 numbers NOT present:
#       8   213  333  476  630  747   872  1633
#      38   228  349  477  637  750   874  1634
#      96   236  359  480  640  766   887  1651
#     117   253  369  543  693  771   926  1652
#     132   265  400  575  694  784    to  1653
#     145   298  408  581  715  798  1000  1654
#     160   329  430  615  721  799  1631
#     200   330  448  617  742  816  1632
#-------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------
      R  R                  D  D                EpRA  EpDE                                             
 FK5 Ah Am    RAs    pmRA  Ed Em   DEs    pmDE -1900 -1900  Vmag Sp DM            SAO     HD BFno      name
---------------------------------------------------------------------------------------------------------------------------
 904  0  1 35.659 -01.877 -77  3 56.56 -017.69 56.87 45.25  4.78 K0 CP-77 1596 258207 224889 THE  OCT  
1630  0  1 57.631 +00.342 - 6  0 50.70 -004.11 49.94 39.84  4.41 M3 SD-06 6345 147042 224935 30   PSC  
 905  0  3 44.391 +00.184 -17 20  9.59 -000.91 42.46 36.51  4.55 A0 BD-18 6417 147059 225132 2    CET  
1001  0  4 41.294 +00.576 -71 26 12.84 -001.44 62.33 51.95  5.59 B9 CP-72 2800 255631 225253           
1002  0  5 20.144 -00.058 - 5 42 27.41 +008.87 53.86 41.98  4.61 K0 SD-06 6357 128572 000028 33   PSC  
1003  0  6 50.100 +00.728 -23  6 27.18 -004.51 61.40 53.63  6.18 F0 CD-23    4 166053 000203           
   1  0  8 23.265 +01.039 +29  5 25.58 -016.33 43.31 33.00  2.06 A0 BD+28    4 073765 000358 ALP  AND  ALPHERATZ
   2  0  9 10.695 +06.827 +59  8 59.18 -018.09 54.34 42.22  2.27 F5 BD+58    3 021133 000432 BET  CAS  CAPH
   3  0  9 24.659 +01.186 -45 44 50.79 -018.11 58.56 45.98  3.88 K0 CD-46   18 214983 000496 EPS  PHE  
   4  0 10 19.257 +00.074 +46  4 20.21 +000.03 56.07 47.67  5.03 F0 BD+45   17 036123 000571 22   AND  
---------------------------------------------------------------------------------------------------------------------------
