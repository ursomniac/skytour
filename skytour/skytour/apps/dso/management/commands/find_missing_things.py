
from django.core.management.base import BaseCommand
from django.db.models import Count
from ...models import DSO

def show_list(dsos, ip=False, header="DSOs missing info"):
    print(header)
    for d in dsos:
        s = f"{d.pk:>5} "
        s += f"{d.imaging_checklist_priority} " if ip else ''
        s += f"{d.shown_name:20s}"
        print(s)

def process_list(d, dsos, idx, ip=False):
    empty = [' ', ' ', ' ', ' ', ' '] # indexed by idx
    if ip:
        empty.append(' ')
    for dso in dsos:
        k = f"{dso.pk:06d}"
        if k not in d.keys():
            d[k] = dict(
                dso=dso,
                flags=empty
            )
        d[k]['flags'][idx] = 'X'
        if ip:
            d[k]['flags'][5] = dso.imaging_checklist_priority
    return d

class Command(BaseCommand):
    help = 'Find missing images and charts'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true')
        parser.add_argument('--wide', action='store_true')
        parser.add_argument('--narrow', action='store_true')
        parser.add_argument('--finder', action='store_true')
        parser.add_argument('--pdf', action='store_true')
        parser.add_argument('--images', action='store_true')
        parser.add_argument('--show', action='store_true')
        parser.add_argument('--imgpri', action='store_true')

    def handle(self, *args, **options):
        wide = DSO.objects.filter(dso_finder_chart_wide='')
        narrow = DSO.objects.filter(dso_finder_chart_narrow='')
        finder = DSO.objects.filter(dso_finder_chart='')
        pdf = DSO.objects.filter(pdf_page='')
        zz = DSO.objects.annotate(image_count=Count('images'))
        no_images = zz.filter(image_count=0)
        ip = options['imgpri']

        if options['wide']:
            print(f"{wide.count()} DSOs are missing wide-field charts")
            if options['show']:
                show_list(wide, ip=ip, header='Missing Wide FOV Charts:')
        if options['narrow']:
            print(f"{narrow.count()} DSOs are missing narrow-field charts")
            if options['show']:
                show_list(narrow, ip=ip, header="Missing Narrow FOV Charts:")
        if options['finder']:
            print(f"{finder.count()} DSOs are missing Finder Charts")
            if options['show']:
                show_list(finder, ip=ip, header="Missing Finder Charts:")
        if options['pdf']:
            print(f"{pdf.count()} DSOs are missing PDF pages")
            if options['show']:
                show_list(pdf, ip=ip, header="Missing PDF Files:")

        if options['images']:
            print(f"{no_images.count()} DSOs have no images")
            if options['show']:
                show_list(no_images, ip=ip, header="No Images:")
                
        if options['all']:
            dsos = {}
            dsos = process_list(dsos, wide, 0, ip=ip)
            dsos = process_list(dsos, narrow, 1, ip=ip)
            dsos = process_list(dsos, finder, 2, ip=ip)
            dsos = process_list(dsos, pdf, 3, ip=ip)
            dsos = process_list(dsos, no_images, 4, ip=ip)

            colnames = ['PK', 'Name', 'Wide', 'Narrow', 'Finder', 'PDF', 'Img']
            if ip:
                colnames.append('IP')
            cols = '\t'.join()
            print("Missing Grid")
            print (cols)
            for k in sorted(dsos.keys()):
                dso = dsos[k]['dso']
                things = '\t'.join(dsos[k]['flags'])
                print(f"{dso.pk:>5}\t{dso.shown_name:20s}\t{things}")


