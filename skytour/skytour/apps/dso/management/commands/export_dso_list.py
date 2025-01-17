from django.core.management.base import BaseCommand
from ...models import DSO

IMGPRI = ['Lowest', 'Low', 'Medium', 'High', 'V. High'] # 0-4
IMGVIA = [
    'Not Viable',      # 0
    'Unlikely Viable', # 1
    'Extremely Diff.', # 2
    '(Very) Diff.',    # 3
    'Challenging',     # 4
    'Req. Patience',   # 5
    'Gen. Visible',    # 6
    'Usually Easy',    # 7
    'Easy',            # 8
    'Very Easy',       # 9
    'Extremely Easy'   # 10
]

def mode_definitions():
    MODES = {
        'I': 'Imaging Scope',
        'M': 'Medium Scope',
        'S': 'Small Scope',
        'B': 'Binoculars',
        'N': 'Naked Eye'
    }
    line = 'OBSERVING MODES:\t\t'
    mlist = []
    for mode in 'IMSBN':
        x = f"{mode}: {MODES[mode]}"
        mlist.append(x)
    mm = ', '.join(mlist)
    out = line + mm + '\n'
    return out

def mode_priorities():
    line = 'PRIORITIES:\t\t'
    plist = []
    for i in range(5):
        x = f"{i} = {IMGPRI[i]}"
        plist.append(x)
    pp = ',  '.join(plist)
    out = line + pp + '\n'
    return out

def mode_viabilities():
    line = 'VIABILITIES:\t\t'
    vlist = []
    for i in range(11):
        x = f"{i} = {IMGVIA[i]}"
        vlist.append(x)
    vv = ', '.join(vlist)
    out = line + vv + '\n'
    return out

def construct_top_headers(options):
    fields = ['Names', '', '']
    fields += ['Location', '', '']
    fields += ['Object', '']
    fields += ['Parameters', '', '']
    if options['modes']:
        fields += ['Obs. Modes', '', '', '', '']
    return '\t'.join(fields)

def construct_headers(options):
    header_list = ['Name']
    if options['infield']:
        header_list.append('In Field Of')
    header_list += ['Nickname', 'Con', 'RA', 'Dec', 'Type', 'Morph']
    header_list += ['Ang. Size', 'Mag', 'Surf Br', 'Opp Date']
    if options['modes']:
        header_list += ['Img', 'Med', 'Small', 'Binoc', 'Eye']
    if options['infield']:
        header_list.append('Field to Primary')
    header_list.append('Aliases')
    headers = '\t'.join(header_list)
    return headers

def construct_modes(dso):
    x = []
    modes = dso.targetdso.targetobservingmode_set.all()
    for mode in 'IMSBN':
        o = modes.filter(mode=mode).first()
        if o is not None:
            try:
                x.append(f"p{o.priority} v{o.viable}")
            except:
                x.append('') # something went wrong
        else:
            x.append('') # Not in list
    return x

def defstr(x):
    return str(x) if x is not None else ''

def process_dso(options, dso, field_dso=False):
    fields = []
    # 1. Name section
    fields.append(dso.shown_name)
    if options['infield']:
        if field_dso:
            fields.append(dso.parent_dso.shown_name)
        else:
            fields.append('')
    fields.append(defstr(dso.nickname))
    # 2. Location section
    fields.append(dso.constellation.abbreviation)
    fields.append(dso.ra_text)
    fields.append(dso.dec_text),
    # 3. Object section
    fields.append(dso.object_type.short_name)
    fields.append(defstr(dso.morphological_type))
    # 4. Parameters section
    fields.append(defstr(dso.find_angular_size[0]))
    fields.append(defstr(dso.find_magnitude[0]))
    sb = dso.find_surface_brightness[0]
    if sb is not None:
        fields.append(defstr(f"{sb:.2f}"))
    else:
        fields.append('')
    opp_date = '' if field_dso else dso.opposition_date.strftime("%b %d")
    # 5. Observing section
    fields.append(opp_date)
    if options['modes']:
        if field_dso:
            fields += ['', '', '', '', '']
        else:
            fields += construct_modes(dso)
    # 6. Additional section
    if options['infield']:
        x = f"{dso.primary_distance:.1f}\' at {dso.primary_angle:.0f}°" if field_dso else ''
        fields.append(x)
    fields.append(defstr(dso.alias_list))
    # return the assembled metadata
    return '\t'.join(fields)

class Command(BaseCommand):
    help = 'Export DSO list'

    def add_arguments(self, parser):
        parser.add_argument('--latitude', type=float, nargs='?', default=43.)
        parser.add_argument('--minmag', nargs='?', default=11., type=float)
        parser.add_argument('--minalt', nargs='?', default=20., type=float)
        parser.add_argument('--minsize', default=2., type=float, nargs='?')
        parser.add_argument('--file', type=str, nargs='?', default='DSO_EXPORT.tsv')
        parser.add_argument('--onlymag', action='store_false')
        parser.add_argument('--onlysize', action='store_false')
        parser.add_argument('--infield', action='store_true')
        parser.add_argument('--imaging', action='store_true')
        parser.add_argument('--modes', action='store_true')
        parser.add_argument('--all', action='store_true')


    def handle(self, *args, **options):
        if options['latitude'] > 0.:
            min_lat = options['latitude'] - (90. - options['minalt'])
            max_lat = 90.
        else:
            max_lat = options['latitude'] + (90. - options['minalt']) 
            min_lat = -90.

        if options['all']:
            options['infield'] = True
            options['imaging'] = True
            options['modes'] = True

        #print("OPTIONS: ", options)
        dsos = DSO.objects.all()
        with open(options['file'], 'w') as f:
        
            if options['modes']:
                f.write(mode_definitions())
                f.write(mode_priorities())
                f.write(mode_viabilities())
                f.write('\n')
            top_headers = construct_top_headers(options)
            headers = construct_headers(options)
            f.write(f"{top_headers}\n")
            f.write(f"{headers}\n")

            for dso in dsos:
                if not options['all']:
                    if dso.dec_float < min_lat or dso.dec_float > max_lat:
                        continue
                    # Magnitude test
                    if dso.magnitude is not None and dso.magnitude > options['minmag']:
                        continue
                    if dso.magnitude is None and options['onlymag']:
                        continue
                    # Size test
                    if dso.major_axis_size is not None and dso.major_axis_size < options['minsize']:
                        continue
                    if dso.major_axis_size is None and options['onlysize']:
                        continue

                rec = process_dso(options, dso, field_dso=False)
                f.write(f"{rec}\n")

                if options['infield']:
                    fdsos = dso.dsoinfield_set.order_by('ra_h', 'ra_m', 'ra_s')
                    for fdso in fdsos:
                        rec = process_dso(options, fdso, field_dso=True)
                        f.write(f"{rec}\n")
                    

                



