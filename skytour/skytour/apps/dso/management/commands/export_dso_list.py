from django.core.management.base import BaseCommand
from ...models import DSO, DSOInField

def defstr(x):
    return str(x) if x is not None else ''

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

    def handle(self, *args, **options):
        if options['latitude'] > 0.:
            min_lat = options['latitude'] - (90. - options['minalt'])
            max_lat = 90.
        else:
            max_lat = options['latitude'] + (90. - options['minalt']) 
            min_lat = -90.

        print("OPTIONS: ", options)
        dsos = DSO.objects.all()
        with open(options['file'], 'w') as f:
        
            header_list = [
                'Name', 'Nickname', 'Con.', 'RA', 'Dec', 'Type', 'Morph.',
                'Ang. Size', 'Mag.', 'Surf. Br.', 'Opp. Date', 'Aliases'
            ]
            headers = '\t'.join(header_list)
            f.write(f"{headers}\n")
            for dso in dsos:
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

                
                # OK - add this DSO
                fields = [
                    dso.shown_name,
                    defstr(dso.nickname),
                    dso.constellation.abbreviation,
                    dso.ra_text,
                    dso.dec_text,
                    dso.object_type.short_name,
                    defstr(dso.morphological_type),
                    defstr(dso.angular_size),
                    defstr(dso.magnitude),
                    defstr(dso.surface_brightness),
                    dso.opposition_date.strftime("%b %d"),
                    defstr(dso.alias_list)
                ]
                rec = '\t'.join(fields)
                f.write(f"{rec}\n")
                    

                



