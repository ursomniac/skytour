from ..models import BrightStar

# TODO V2.x: Move this to a ./seed script library
"""
This just exists to load the BrightStar table from a text dump of the BSC file.
Once it's in the database, this is no longer necessary.
"""
def tr(line, col, length, type):
    start = col-1
    end = col-1+length
    str = line[start:end]
    if str.isspace() or str == '':
        return None
    if type == 'int':
        return int(str)
    elif type == 'float':
        str.replace('+', ' ')
        return float(str)
    return str.strip()

SKIP = [92, 95, 182, 1057, 1841, 2472, 2496, 3515, 3671, 6309, 6515, 7189, 7539, 8296]
def load_bsc():
    with open('skytour/apps/stars/data/bsc5.dat') as f:
        lines = f.readlines()

    for line in lines:
        hr_id = tr(line, 1, 4, 'int')
        if hr_id in SKIP:
            continue
        print ("Processing: ", hr_id)
        star = BrightStar.objects.filter(hr_id=hr_id).first() or BrightStar()
        star.pk = hr_id
    # hr_id = models.PostitiveIntegerField(_('HR #'))
        star.hr_id = hr_id
    # flamsteed = models.CharField(_('Flamsteed'), max_length = 10, null=True, blank=True)
        star.flamsteed = tr(line, 5, 3, 'str')    
    # bayer = models.CharField(_('Bayer'), max_length=10, null=True, blank=True)
        star.bayer = tr(line, 8, 4, 'str')
    # constellation = models.CharField(_('Constellation'), max_length = 3,null = True, blank = True)
        star.constellation = tr(line, 12, 3, 'str')
    # bd_id = models.CharField(_('BD #'), max_length=11, null = True, blank = True)
        star.bd_id = tr(line, 15, 11, 'str')
    # hd_id = models.PositiveIntegerField( _('HD #') ,  null=True, blank=True)
        star.hd_id = tr(line, 26, 6, 'int')
    # sao_id = models.PositiveIntegerField(_ ('SAO #'), null=True, blank=True)
        star.sao_id = tr(line, 32, 6, 'int')
    # fk5_id = models.PositiveIntegerField( _('FK5 #'), null=True, blank=True)
        star.fk5_id = tr(line, 38, 4, 'int')
    # double_star = models.CharField(_('Double Star Code'), max_length=1, blank=True, null=True)
        star.double_star = tr(line, 44, 1, 'str')
    # ads_id = models.CharField(_('ADS Designation'), max_length=5, null=True, blank=True)
        star.ads_id = tr(line, 45, 5, 'str')
    # var_id = models.CharField(_('Var. Star ID'), max_length=9, null=True, blank=True)
        star.ads_components = tr(line, 50, 2, 'str')
        star.var_id = tr(line, 52, 9, 'str')
    # ra_h, ra_m, ra_s, dec_sign, dec_d, dec_m, dec_s in Coordinate abstract class 
        star.ra_h = tr(line, 76, 2, 'int')
        star.ra_m = tr(line, 78, 2, 'int')
        star.ra_s = tr(line, 80, 4, 'float')
        star.dec_sign = tr(line, 84, 1, 'str')
        star.dec_d = tr(line, 85, 2, 'int')
        star.dec_m = tr(line, 87, 2, 'int')
        star.dec_s = tr(line, 89, 2, 'float')
    # gal_long = models.FloatField(_('Gal. Long.'), blank=True, null=True)
        star.gal_long = tr(line, 91, 6, 'float')
    # gal_lat = models.FloatField(_('Gal. Lat.'), null=True, blank=True)
        star.gal_lat = tr(line, 97, 5, 'float')
    # magnitude = models.FloatField(_('V Mag.'), blank=True, null=True)
        star.magnitude = tr(line, 103, 5, 'float')
    # b_v = models.FloatField(_('B-V'), null=True, blank=True)
        star.b_v = tr(line, 110, 5, 'float')
    # u_b = models.FloatField(_('U-B'), null=True, blank=True)
        star.u_b = tr(line, 116, 5, 'float')
    # r_i = models.FloatField(_('R-I'), null=True, blank=True)
        star.r_i = tr(line, 122, 5, 'float')
    # spectral_type = models.CharField(_('Spectral Type'), max_length=20, null=True, blank=True)
        star.spectral_type = tr(line, 128, 20, 'str')
    # spt_code = models.CharField(_('Sp. Type Code'), max_length=1, null=True, blank=True)
        star.spt_code = tr(line, 148, 1, 'str')
    # pm_ra = models.FloatField(_('Prop. Motion RA'), null=True, blank=True)
        star.pm_ra = tr(line, 149, 6, 'float')
    # pm_dec = models.FloatField(_('Prop. Motion Dec.'), null=True, blank=True)
        star.pm_dec = tr(line, 155, 6, 'float')
    # parallax_flag = models.CharField(_('Parallax Flag'), max_length=1, null=True, blank=True)
        star.parallax_flag = tr(line, 161, 1, 'str')
    # parallax = models.FloatField(_('Parallax'), null=True, blank=True)
        star.parallax = tr(line, 162, 5, 'float')
    # radial_velocity = models.FloatField(_('Radial Velocity'), null=True, blank=True)
        star.radial_velocity = tr(line, 177, 3, 'int')
    # rv_flag = models.CharField(_('RV Flag'), max_length=1, null=True, blank=True)
        star.rv_flag = tr(line, 171, 1, 'str')
    # rot_flag = models.CharField(_('Rot. Vel. Flag'), null=True, blank=True)
        star.rot_flag = tr(line, 175, 2, 'str')
    # vsini = models.PositiveIntegerField(_('v sin i'), null=True, blank=True)
        star.vsini = tr(line, 177, 3, 'int')
    # d_mag = models.FloatField(_('d Mag (double)'), null=True, blank=True)
        star.d_mag = tr(line, 181, 4, 'float')
    # ang_sep = models.FloatField(_('Ang. Sep.'), null=True, blank=True)
        star.ang_sep = tr(line, 185, 6, 'float')
    # notes = models.BooleanField(_('Notes'), default=False)
        notes = tr(line, 197, 1, 'str')
        if notes != '':
            star.notes = True

        star.save()

def old_load_names():
    with open('skytour/apps/stars/data/star_names.txt') as f:
        lines = f.readlines()

    for line in lines:
        if line[0] == '#':
            continue # skip headers
        if len(line) < 103:
            continue # skip
        hd = tr(line, 86, 6, 'int')
        name = line[103:].title()
        star = BrightStar.objects.filter(hd_id=hd).first()
        if star:
            star.proper_name = name
            star.save()

def load_names():
    with open('skytour/apps/stars/data/star_names.tsv') as f:
        lines = f.readlines()

    for line in lines:
        star = None
        if 'Bayer' in line:
            continue # header
        (star_id, constellation, other, name, explanation) = line.split('\t')[:5]
        if len(star_id) == 0:
            if 'HD' in other:
                hd_id = other.split(' ')[1]
                star = BrightStar.objects.filter(hd_id=int(hd_id)).first()
                if not star:
                    #print ("Can't find: HD: ", hd_id)
                    continue # didn't find a match
            else:
                #print ("Skipping: ", other)
                continue
        else:
            if not star_id[0].isdigit():  # Bayer
                star = BrightStar.objects.filter(bayer=star_id, constellation=constellation).first()
            else: # Flamsteed
                star = BrightStar.objects.filter(flamsteed=star_id, constellation=constellation).first()
        if not star:
            #print("Can't find: ID:{} C:{}".format(star_id, constellation, other))
            continue
        # Have a star
        star.proper_name = name
        star.name_explanation = explanation
        star.save()
        