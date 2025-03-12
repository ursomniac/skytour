import re
from ...utils.models import Constellation
from ..models import VariableStar, StarCatalog
from ..vocabs import GCVS_ID as LOOKUP_GCVS

# TODO V2.x: Move this to a ../../seed script library
def tr(line, col, length, type):
    """
        eg:  tr(line, 15, 3, 'str') gets an A3 from line[14:16]
    """
    p = re.compile("[+-]?[0-9]+\.?[0-9]*")
    start = col-1
    end = col-1+length
    str = line[start:end]
    if str.isspace() or str == '':
        return None
    if type == 'int':
        return int(str)
    elif type == 'float':
        #str.replace('+', ' ')
        try:
            str = p.search(str).group()
        except:
            print("Cannot parse ", str)
        return float(str)
        #return float(str)
    return str.strip()

def get_remarks():
    d = {}
    with open('data/gcvs_51/gcvs_remark.txt') as f:
        lines = f.readlines()
    #print(f"There are {len(lines)} lines")
    f.close()
    for line in lines:
        #012345678901234567890
        #PU    Cnc    P1 is presented in the Table. P0 = 0.489181d; P1/P0 = 0.7443.
        id = line[:10]
        comment = line[13:]
        if id not in d.keys():
            d[id] = []
        d[id].append(comment)
    return d

def load_gcvs(debug=True):
    """
    GCVS file format:
        Col     Fmt   Units    Label     Notes


        132-134 A3     %       M-m/D     Rising time (M-m) or eclipse duration (D)
        135     A1             u_M-m/D   uncertainty on M-m/D
        136     A1             n_M-m/D   Note for Eclipsing Variable

        168-178 A12            Exists    Cases to non-existence of var
        180-185 F6.3   "/yr    PMa       Proper Motion RA
        187-192 F6.3   "/yr    PMd       Proper Motion Dec
        194-201 F8.3   year    EpochCoor Epoch of the Coordinates
        203     A1             u_Ident   Uncertainty Flag on ID
        205-213 A12            Ident     Source of astrometric data
        226-235 A10            GCVS2     Var star Designation
    """
    gcvs_cat = StarCatalog.objects.get(slug='gcvs')
    with open('data/gcvs_51/gcvs5.txt') as f:
        lines = f.readlines()
    f.close()

    if debug:
        print(f"THERE ARE {len(lines)} LINES.")

    notes = get_remarks()
    if debug:
        print(f"{len(notes.keys())} stars have remarks.")

    for line in lines:
        # COLUMNS FORMAT UNITS   FIELD     DESCRIPTION

        ### Identification
        # 1-2     I2             Constell  Constellation ID
        # 3-6     I4             Number    Star # in constellation
        # 7       A1             Component Component ID
        gcvs_id = tr(line, 1, 7, 'str')
        star = VariableStar.objects.filter(id_in_catalog=gcvs_id).first() or VariableStar()
        star.catalog = gcvs_cat
        star.id_in_catalog = gcvs_id # will add if new
        constellation_id = tr(line, 1, 2, 'int')
        star.constellation = Constellation.objects.get(pk=constellation_id)
        # 9-18    A10            GCVS      V* Designation
        # |omi 1 CMa
        # |EQ    PEGA
        var_con = tr(line, 15, 3, 'str')
        var_designation = tr(line, 7, 1, 'str') # number or letter
        if line[2] != '9':
            var_id = tr(line, 9, 5, 'str')
            if var_id[:2] == 'V0':
                var_id.replace('V0', 'V')
            lookup_var_id = var_id
            name = f"{var_id} {star.constellation.abbr_case}"
        else:
            lookup_id = tr(line, 3, 4, 'str')
            var_id = LOOKUP_GCVS[lookup_id] 
            lookup_var_id = tr(line, 9, 5, 'str')
            num = tr(line, 13, 1, 'str')
            name = f"{var_id}"
            if num is not None and num != ' ':
                name += f" {num}"
            name += f" {star.constellation.abbr_case}"
        star.variable_id = f"{var_id} {var_con}"
        if var_designation is not None and len(var_designation) > 0:
            star.variable_id += f" {var_designation}"
        ref_lookup = f"{lookup_var_id:5s} {star.constellation.abbr_case}"
        ref_lookup = ref_lookup.replace('.', ' ')
        if var_designation in ['A', 'B']:
            name += f" {var_designation}"
            ref_lookup += var_designation
        else:
            ref_lookup += ' '

        star.name = name
        if debug and line[6] != ' ':
            print(f"GCVS: {gcvs_id} NAME: [{name}]")
        ### Position
        # 21-22   I2     h       RAh       J2000 RA Hours
        # 23-24   I2     m       RAm       J2000 RA Minutes
        # 25-29   F5.2   s       RAs       J2000 RA Sec
        # 31      A1             DE-       J2000 Dec Sign (+,-)
        # 32-33   I2     deg     DEd       J2000 Dec Degrees
        # 34-35   I2     arcmin  DEm       J2000 Dec Arcminutes
        # 36-39   F4.1   arcsec  DEs       J2000 Dec Arcseconds
        test_if_exists = tr(line, 21, 18, 'str')
        if test_if_exists is None:
            continue # This star does not exist or is a duplicate.
        star.ra_h = tr(line, 21, 2, 'int')
        star.ra_m = tr(line, 23, 2, 'int')
        star.ra_s = tr(line, 25, 5, 'float')
        star.dec_sign = tr(line, 31, 1, 'str')
        star.dec_d = tr(line, 32, 2, 'int')
        star.dec_m = tr(line, 34, 2, 'int')
        star.dec_s = tr(line, 36, 4, 'float')
        ### Spectral Type
        # 138-154 A17            SpType    Spectral Type
        star.spectral_type = tr(line, 138, 17, 'str')

        ### VARIABLE TYPE
        # 42-51   A10            VarType   Type of Variability (need CV for this)
        star.type_original = tr(line, 42, 10, 'str')
        # 215-224 A10            VarType2  NEW type of variability
        star.type_revised = tr(line, 215, 10, 'str')

        ### MAGNITUDES
        # 53      A1             l_magMax  [<>*(]">" if magMax is a faint limit "<" if bright limit
        star.mag_max_limit = tr(line, 53, 1, 'str')
        # 54-59   F6.3   mag     magMax    Mag at max brightness
        star.mag_max = tr(line, 54, 5, 'float')
        # 60      A1             u_magMax  Uncertainty Flag of magMax
        star.mag_max_uncertainty = tr(line, 60, 1, 'str')

        # 63-64   A2             l_magMin1 [<(]"<" if magMin1 is a bright limit; '(' if amplitude
        # 74      A1             f_magMin1 [)] ")" if magMinI is an amplitude
        # 65-70   F6.3   mag     magMin1   Mag Min 1        
        min1_limit = tr(line, 63, 2, 'str')
        min1_lim2 = tr(line, 74, 1, 'str')
        min1_mag = tr(line, 65, 5, 'float')
        if min1_limit is not None and '(' in min1_limit and min1_lim2 is not None and min1_lim2 == ')': # amplitude
            star.mag_min1_amplitude = min1_mag
        else:
            star.mag_min1_limit = min1_limit
            star.mag_min1 = min1_mag
        # 71      A1             u_magMin1 Uncertainty flag on magMin1
        # 72-73   A2             n_magMin1 Alt. Mag system for magMin1
        star.mag_min1_uncertainty = tr(line, 71, 1, 'str')
        star.mag_min1_system = tr(line, 72, 2, 'str')
        # 76-77   A2             l_magMin2 [<(]"<" if magMinI is a bright limit; '(' if amplitude
        # 78-83   F6.3   mag     magMin2   Mag Min 2
        # 84      A1             u_magMin2 Uncertainty flag on magMin2
        # 85-86   A2             n_magMin2 Alt. Mag system for magMin2
        # 87      A1             f_magMin2 [)] ")" if magMin2 is an amplitude
        min2_limit = tr(line, 76, 2, 'str')
        min2_lim2 = tr(line, 87, 1, 'str')
        min2_unc = tr(line, 84, 1, 'str')
        # NO Ara has a weird Min2
        mm2 = tr(line, 78, 6, 'str')
        min2_mag = None
        if mm2 is not None:
            if 'V' in mm2:
                mm2 = mm2.replace('V', ' ')
            if ':' in mm2:
                mm2 = mm2.replace(':', ' ')
            if 'I' in mm2:
                mm2 = mm2.replace('I', ' ')
                min2_unc = ':'
            min2_mag = tr(mm2, 1, 6, 'float')
        if min2_limit is not None and '(' in min2_limit and min2_lim2 is not None and min2_lim2 == ')': # amplitude
            star.mag_min2_amplitude = min2_mag
        else:
            star.mag_min2_limit = min2_limit
            star.mag_min2 = min2_mag
        star.mag_min2_uncertainty = min2_unc
        
        # 89-90   A2             mag_code  Photometric System for Magnitudes
        star.mag_code = tr(line, 89, 2, 'str')
        
        ### PERIOD
        # 92-102  F11.5  JD      Epoch     Epoch for Maximum light; JD
        # 103     A1             q_Epoch   [:+-] Quality flag on Epoch
        epoch_str = tr(line, 92, 12, 'str')
        if epoch_str is not None:
            if ':' in epoch_str:
                epoch_str = epoch_str.replace(':', ' ')
                star.epoch_quality = ':'
            star.epoch_jd = tr(epoch_str, 1, 11, 'float')
        # 105-108 A4             YearNova  Year of outburst for nova or supernova
        star.year_nova = tr(line, 105, 4, 'int')
        # 109     A1             q_Year    [:] quality flag on YearNova
        star.year_nova_quality = tr(line, 109, 1, 'str')
        # 111     A1             l_Period  [<>(] Code for upper/lower limits on Period
        # 112-127 F16.10 d       Period    Period of Variable Star
        # 128     A1             u_Period  uncertainty flag on Period
        # 129-130 A2             n_Period  [*/N)]
        period_str = tr(line, 111, 20, str)
        if period_str is not None:
            period_str = period_str.replace(' ','')
            period_str = period_str.replace('*2', '*')
            unc = ''
            for bad in ':(N/':
                if bad in period_str:
                    unc += bad
                    period_str = period_str.replace(bad, '')
            star.period = tr(period_str, 1, len(period_str), 'float')

            star.period_uncertainty = unc
        # REFERENCES
        # 156-160 A5             Ref1      Ref to study of star
        # 162-166 A5             Ref2      Ref to chart or photograph
        ### NOTES
        # 19      A1             NoteFlag  ref to Remarks file
        remarks_flag = tr(line, 19, 1, 'str') == '*'
        if remarks_flag:
            if ref_lookup not in notes.keys():
                continue # some entries have the * for notes but there aren't any...
            else:
                star.notes = ''
                for remark in notes[ref_lookup]:
                    star.notes += f"{remark}\n"
        # 40      A1             u_DEs     position accuracy flag
        position_flag = tr(line, 40, 1, 'str') == ':'

        if not debug:
            star.save()
            print(f"Saving {star}")
        else:
            if star.name[0] not in 'ABCDEFGHJIJKLMNOPQRSTUVWXYZ':
                print(f"Doing {star.name}")

def add_slug():
    # 01234567890
    # 12345678901
    # mu. 2 90122
    with open('data/gcvs_51/id_decode.txt') as f:
        lines = f.readlines()
    f.close()
    d = {}
    for line in lines:
        line = line.strip()
        k = line[6:]
        n = '' if len(line) < 11 else line[10]
        g = tr(line, 1, 5, 'str')
        d[k] = f"{g}{n}"

    vv = VariableStar.objects.all()
    for v in vv:
        gcvs = v.id_in_catalog
        const = v.constellation.abbreviation.lower()
        k = gcvs[2:]
        if k > '0334' and k[0] != '9':
            if k[0] == '0':
                k = k[1:]
            id = f"v{k}"
        else:
            if k[-1] in 'AB':
                x = k[-1]
                k = k[:-1]
            else:
                x = ''
            if k not in d.keys():
                print (f"ERROR FINDING {k}")
                print(f"V = {v}")
                break
            id = d[k]
            id = id.replace('.', '')
            id = id.strip()
            id = id.split(' ')[0]
            if ' ' in id:
                print(f"ERROR IN ID: {id}")
                print(f"V = {v}")
                break
        slug = f"{gcvs.lower()}-{const}-{id.lower()}"
        if x != '':
            slug += f'-{x.lower()}'
        v.slug = slug
        v.save()

