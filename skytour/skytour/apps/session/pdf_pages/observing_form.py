from ...site_parameter.helpers import find_site_parameter
from .utils import do_line
from .vocabs import PAGE_WIDTH

def do_observing_form(p, context):
    num_pages = find_site_parameter('pdf-observing-form-pages', 2, 'positive')
    if num_pages < 1:
        return p # do Nothing

    for i in range(num_pages):
        y = 720
        p.setFont('Helvetica-Bold', 14)
        p.drawString(50, y, 'Observation Forms:')
        p.setFont('Helvetica-Bold', 12)
        y -= 20

        # Make some lines
        section_tops = [700, 500, 300, 100]
        for ly in section_tops:
            p.line(40, ly, PAGE_WIDTH-20, ly)

        for section in range(3):
            y = section_tops[section] - 20
            p.setFont('Helvetica-Bold', 12)
            ## Column 1: 
            for ll in [
                'TIME: ____________________',
                'OBJECT: __________________',
                'OBJ TYPE: ________________',
                'CONST: ___________________',
                'EYEPS: ___________________',
                'FILTERS: _________________',
            ]:
                p, y = do_line(p, 50, y, ll, dy=22)


            ## Column 2:
            y = section_tops[section] - 20
            notes = ['NOTES: _________________'] + \
                5 * ['________________________']
            for ll in notes:
                p, y = do_line(p, 250, y, ll, dy=22)

            y -= 10
            p.setFont('Helvetica-Bold', 9)
            p, y = do_line(p,  50, y, 'SQM: __________', dy=0)
            p, y = do_line(p, 150, y, 'Temp: _________', dy=0)
            p, y = do_line(p, 250, y, 'RH%: __________', dy=0)
            p, y = do_line(p, 350, y, 'Wind: _________', dy=0)
            p, y = do_line(p, 450, y, 'Clouds: _______________', dy=20)
            p, y = do_line(p,  50, y, 'Seeing: _______', dy=0)
            p, y = do_line(p, 150, y, 'Notes: ____________________________________________________________________', dy=0)

        # Column 3:
        # Drawing circle
            p.circle(500, section_tops[section]-80, 72)

        p.showPage()
    return p