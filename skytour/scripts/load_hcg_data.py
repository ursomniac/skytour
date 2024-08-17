from skytour.apps.dso.models import DSO, DSOInField, DSOImagingChecklist
from skytour.apps.utils.models import Catalog, Constellation, ObjectType

primary = """hcg,name,J2000,con,type,n,size,tot_r_mag,mpc,czall,n1
  1,HCG   1,J002600.22+254304.9,AND,S3,4,2.9,12.8,476.7,0.0339,4
  2,HCG   2,J003135.83+082617.0,PSC,S2,4,7.1,12.1,202.5,0.0144,3
  3,HCG   3,J003411.48-073535.4,CET,S2,4,3.8,12.3,358.6,0.0255,3
  4,HCG   4,J003415.98-212648.4,CET,S1,5,3.6,12.5,393.7,0.028,3
  5,HCG   5,J003854.10+070348.7,PSC,S2,4,1.6,12.5,576.6,0.041,3
  6,HCG   6,J003910.13-082343.8,CET,E3,4,1.6,12.3,533.0,0.0379,4
  7,HCG   7,J003923.92+005241.0,CET,E2,4,5.7,11.4,198.3,0.0141,4
  8,HCG   8,J004936.81+233450.7,AND,E2,4,1.2,12.3,766.4,0.0545,4
  9,HCG   9,J005418.05-233304.8,CET,E1,4,2.1,13.1,0.0,,
 10,HCG  10,J012607.39+344127.0,AND,S3,4,10.9,10.1,226.4,0.0161,4
 11,HCG  11,J012634.27-231352.7,CET,S1,4,4.9,12.1,0.0,,
 12,HCG  12,J012733.71-044014.3,CET,E1,5,2.6,12.9,682.0,0.0485,5
 13,HCG  13,J013222.13-075252.2,CET,E2,5,2.5,13.3,578.0,0.0411,5
 14,HCG  14,J015947.63-070143.2,CET,S3,4,6.7,12.1,257.3,0.0183,3
 15,HCG  15,J020739.00+020817.4,CET,E3,6,7.7,11.7,320.6,0.0228,6
 16,HCG  16,J020931.29-100930.8,CET,S3,4,6.4,10.2,185.6,0.0132,4
 17,HCG  17,J021406.34+131847.4,ARI,E3,5,1,13.7,848.0,0.0603,5
 18,HCG  18,J023906.81+182259.0,ARI,S2,4,2,12.7,0.0,,
 19,HCG  19,J024245.16-122442.8,CET,E3,4,3.1,12.1,0.0,,
 20,HCG  20,J024415.00+260610.4,ARI,S3,6,1.5,13,680.6,0.0484,5
 21,HCG  21,J024517.75-173710.2,ERI,S3,5,10.8,10.1,353.0,0.0251,3
 22,HCG  22,J030331.29-154032.8,ERI,E1,5,5,10.5,126.6,0.009,3
 23,HCG  23,J030706.50-093508.0,ERI,S3,5,7.1,11.2,226.4,0.0161,4
 24,HCG  24,J032018.89-105153.0,ERI,E2,4,2.4,12.7,428.9,0.0305,5
 25,HCG  25,J032043.74-010307.2,CET,S3,7,6.4,11.8,298.1,0.0212,4
 26,HCG  26,J032154.22-133845.4,ERI,S2,4,1.9,12.7,444.4,0.0316,7
 27,HCG  27,J041921.19-114235.3,ERI,S3,5,3.8,14,1229.0,0.0874,4
 28,HCG  28,J042719.54-101900.0,ERI,S1,4,1.2,13.2,534.4,0.038,3
 29,HCG  29,J043446.02-303249.9,ERI,S2,4,0.8,14.8,1472.3,0.1047,3
 30,HCG  30,J043628.62-024956.8,ERI,S3,4,4.5,11.6,216.6,0.0154,4
 31,HCG  31,J050136.91-041524.2,ERI,S2,4,0.9,13.5,192.7,0.0137,3
 32,HCG  32,J050142.91-152512.1,LEP,E1,4,3,12.7,573.7,0.0408,4
 33,HCG  33,J051047.93+180204.6,TAU,E3,4,2.1,12.4,365.6,0.026,4
 34,HCG  34,J052147.42+064036.8,ORI,E1,4,1.2,12.7,431.7,0.0307,4
 35,HCG  35,J084519.55+443118.1,LYN,S3,6,2.2,12.4,762.2,0.0542,6
 36,HCG  36,J090923.73+154744.4,CNC,S1,4,1.9,12.5,0.0,,
 37,HCG  37,J091335.67+300051.3,CNC,E2,5,3.2,11.5,313.6,0.0223,5
 38,HCG  38,J092738.88+121651.3,LEO,S3,4,2.9,12.5,410.6,0.0292,3
 39,HCG  39,J092928.90-012039.3,HYA,E2,4,1,13.9,985.8,0.0701,4
 40,HCG  40,J093854.50-045106.3,HYA,E2,6,1.7,11.4,313.6,0.0223,5
 41,HCG  41,J095739.56+451422.3,UMA,S1,4,4.1,11.9,0.0,,
 42,HCG  42,J100017.49-193840.2,HYA,E1,4,6,10.6,187.0,0.0133,4
 43,HCG  43,J101113.81-000153.5,SEX,S2,5,3.5,12.4,464.1,0.033,5
 44,HCG  44,J101800.51+214844.1,LEO,S2,4,16.4,9.3,64.7,0.0046,4
 45,HCG  45,J101911.27+590635.0,UMA,S1,4,3.4,13.5,1029.4,0.0732,3
 46,HCG  46,J102201.84+174853.9,LEO,E3,4,3.6,12.3,379.7,0.027,4
 47,HCG  47,J102548.40+134354.3,LEO,S1,4,2.3,12.5,445.8,0.0317,4
 48,HCG  48,J103745.60-270450.0,HYA,E1,4,5,11.6,132.2,0.0094,3
 49,HCG  49,J105636.49+671045.5,UMA,E2,4,0.9,14.4,466.9,0.0332,4
 50,HCG  50,J111706.14+545507.1,UMA,E2,5,0.7,14.4,1957.5,0.1392,5
 51,HCG  51,J112220.90+241735.8,LEO,E2,6,4.5,11.5,362.8,0.0258,5
 52,HCG  52,J112618.71+210521.0,LEO,S1,4,3.2,12.8,604.7,0.043,3
 53,HCG  53,J112858.36+204635.3,LEO,S1,4,12.9,11.5,289.7,0.0206,3
 54,HCG  54,J112915.30+203443.2,LEO,E2,4,0.7,14.3,68.9,0.0049,4
 55,HCG  55,J113207.52+704843.0,DRA,E3,5,0.9,13.4,739.7,0.0526,4
 56,HCG  56,J113231.92+525655.4,UMA,S3,5,2.1,12.2,379.7,0.027,5
 57,HCG  57,J113750.49+215906.2,LEO,S2,8,5.5,11.4,427.5,0.0304,7
 58,HCG  58,J114211.80+101901.7,LEO,S3,5,8.8,12.6,291.1,0.0207,5
 59,HCG  59,J114825.63+124334.9,LEO,E3,5,2.1,12.5,189.8,0.0135,4
 60,HCG  60,J120305.10+514135.5,UMA,E2,4,2.3,13.4,878.9,0.0625,4
 61,HCG  61,J121223.95+291040.5,COM,E3,4,3.8,9.9,182.8,0.013,3
 62,HCG  62,J125303.06-091125.9,VIR,E3,4,3.7,11.6,192.7,0.0137,4
 63,HCG  63,J130209.99-324604.9,CEN,S3,4,2.9,13.1,437.3,0.0311,3
 64,HCG  64,J132543.35-035127.6,VIR,S2,4,1.7,13.4,506.2,0.036,3
 65,HCG  65,J132953.94-292958.2,HYA,E1,5,1.7,12.7,668.0,0.0475,5
 66,HCG  66,J133833.58+571816.0,UMA,E1,4,1,13.8,982.9,0.0699,4
 67,HCG  67,J134903.54-071219.2,VIR,E3,4,3.3,11.6,344.5,0.0245,4
 68,HCG  68,J135340.91+401941.0,CVN,E3,5,9.2,9.5,112.5,0.008,5
 69,HCG  69,J135530.08+250426.7,BOO,S2,4,1.9,12.2,413.4,0.0294,4
 70,HCG  70,J140413.21+331940.5,CVN,S2,6,3.4,12.1,894.4,0.0636,4
 71,HCG  71,J141104.60+252906.1,BOO,S1,4,5,12.8,423.3,0.0301,3
 72,HCG  72,J144755.22+190327.2,BOO,E3,5,1.8,11.9,592.0,0.0421,4
 73,HCG  73,J150240.16+232113.6,BOO,S1,5,4.8,12.5,631.4,0.0449,3
 74,HCG  74,J151928.32+205337.1,SER,E2,5,1.9,12.1,561.1,0.0399,5
 75,HCG  75,J152133.84+211100.7,SER,E3,6,2.2,12.4,585.0,0.0416,6
 76,HCG  76,J153141.91+071828.8,SER,S3,5,3.3,12.3,478.1,0.034,7
 77,HCG  77,J154917.30+214942.5,SER,E3,4,0.8,13.8,0.0,,
 78,HCG  78,J154828.04+681227.9,DRA,S3,4,3.5,12.7,0.0,,
 79,HCG  79,J155912.01+204531.3,SER,E3,5,1.3,11.3,203.9,0.0145,4
 80,HCG  80,J155912.41+651333.4,DRA,E2,4,1.7,12.6,435.9,0.031,4
 81,HCG  81,J161813.01+124739.2,HER,E3,4,0.9,13.3,701.7,0.0499,4
 82,HCG  82,J162822.10+324925.3,HER,E2,4,3.1,12.2,509.1,0.0362,4
 83,HCG  83,J163540.91+061611.7,HER,E3,4,1.9,13.8,746.7,0.0531,5
 84,HCG  84,J164408.21+775010.4,UMI,E3,6,2.4,13.5,781.9,0.0556,5
 85,HCG  85,J185022.44+732059.7,DRA,E3,4,1.3,12.8,552.6,0.0393,4
 86,HCG  86,J195159.21-304933.8,SGR,E2,4,4,12.3,279.8,0.0199,4
 87,HCG  87,J204811.88-195026.6,CAP,S1,4,1.5,12.4,416.2,0.0296,3
 88,HCG  88,J205222.82-054528.7,AQR,S3,4,5.2,11.3,282.7,0.0201,4
 89,HCG  89,J212010.83-035432.7,AQR,S2,4,4.8,13.7,417.6,0.0297,4
 90,HCG  90,J220205.60-315760.0,PSA,E3,4,7.4,9.1,123.7,0.0088,4
 91,HCG  91,J220910.40-274744.7,PSA,S1,4,5.2,11.7,334.7,0.0238,4
 92,HCG  92,J223557.53+335735.8,PEG,S2,5,3.2,11.1,302.3,0.0215,4
 93,HCG  93,J231524.26+185858.8,PEG,E3,5,9,10.9,236.2,0.0168,4
 94,HCG  94,J231716.60+184310.4,PEG,E1,7,2.8,12.3,586.4,0.0417,7
 95,HCG  95,J231931.79+092930.2,PEG,E3,4,1.5,11.9,556.9,0.0396,4
 96,HCG  96,J232758.32+084626.3,PEG,S2,4,2.3,11.5,410.6,0.0292,4
 97,HCG  97,J234724.06-021909.0,PSC,E2,5,5.2,11.5,306.6,0.0218,5
 98,HCG  98,J235411.77+002226.4,PSC,E2,4,2.4,11.5,374.1,0.0266,3
 99,HCG  99,J000043.69+282319.7,PSC,S2,4,2.4,12.2,407.8,0.029,5
100,HCG 100,J000120.79+130756.8,PSC,S1,4,3.6,11.5,250.3,0.0178,3"""


def get_catalogs():
    cats = {
        'hcg': Catalog.objects.get(slug='hickson'),
        'ngc': Catalog.objects.get(slug='ngc'),
        'ic':  Catalog.objects.get(slug='index'),
        'ugc': Catalog.objects.get(slug='ugc')
    }
    return cats

def get_fields(line):
    return line.split(',')

def get_value(sign, x,  m, s):
    v = int(x) + int(m)/60. + float(s)/3600.
    v *= -1 if sign == '-' else 1
    return v

def get_radec(j2000):
    rastr = j2000[1:10]
    decstr = j2000[10:]
    rah = rastr[:2]
    ram = rastr[2:4]
    ras = rastr[4:]
    ra = dict(
        h = int(rah),
        m = int(ram),
        s = float(ras),
        value = get_value('+',rah, ram, ras)
    )
    dsign = decstr[0]
    decd = decstr[1:3]
    decm = decstr[3:5]
    decs = decstr[5:]
    dec = dict(
        sign = dsign,
        d = int(decd),
        m = int(decm),
        s = float(decs),
        value = get_value(dsign, decd, decm, decs)
    )
    return ra, dec

def get_line(line):
    fields = line.split('\t')
    return fields

def get_constellation(abbr):
    return Constellation.objects.get(slug=abbr)

def process_group(line, dso, create, hcg_catalog, object_type):
    fields = get_fields(line.strip())
    id_in_cat = fields[0]
    j2000 = fields[2]
    constellation = get_constellation(fields[3])
    subclass = fields[4]
    ra, dec = get_radec(j2000)

    # Build/update DSO
    dso.catalog = hcg_catalog
    dso.id_in_catalog = id_in_cat
    dso.constellation = constellation
    dso.object_type = object_type
    dso.morphological_type = subclass
    dso.priority = 'Low'
    dso.ra_h = ra['h']
    dso.ra_m = ra['m']
    dso.ra_s = ra['s']
    dso.ra = ra['value']
    dso.dec_sign = dec['sign']
    dso.dec_d = dec['d']
    dso.dec_m = dec['m']
    dso.dec_s = dec['s']
    dso.dec = dec['value']
    dso.magnitude = float(fields[7])
    dso.magnitude_system = 'R'
    dso.angular_size = f"{fields[6]}'"
    dso.major_axis_size = float(fields[6])
    dso.minor_axis_size = float(fields[6])
    dso.surface_brightness = None
    dso.contrast_index = None
    dso.orientation_angle = 0.
    dist = float(fields[8])
    dso.distance = dist if dist != 0 else None
    dso.distance_units = 'Mly' if dist != 0 else None
    # other params

    dso.save()
    if create:
        img_priority = DSOImagingChecklist()
        img_priority.dso = dso
        img_priority.priority = 1
        img_priority.save()

    return dso

def process_data(obj_list = []): # send list for UPDATES
    catalog_dict = get_catalogs()
    object_type = ObjectType.objects.get(slug='galaxy--compact-group')

    hcg = primary.split('\n')
    check_list = len(obj_list) != 0

    if check_list:
        ids = check_list
    else:
        ids = list(range(1, 101))

    for id in ids:
        print(f"Doing: {id}")
        create = False
        line = hcg[id]
        dso = DSO.objects.filter(catalog__slug='hickson', id_in_catalog=str(id)).first()
        if check_list:
            if dso is None:
                print(f"Error finding ID {id}")
                continue
        else: # running all DSOs
            if dso is None:
                create = True
                dso = DSO() # new DSO

        dso = process_group(line, dso, create, catalog_dict['hcg'], object_type)



