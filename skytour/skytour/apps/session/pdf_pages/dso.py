from ...astro.local import is_object_up
from ...dso.models import DSO, DSOList
from ...dso.finder import plot_dso_list
from ...dso.helpers import get_map_parameters, get_star_mag_limit
from ...pdf.utils import bold_text, label_and_text, place_text, add_image
from ...pdf.utils import X0, Y0
from ...utils.format import to_hm, to_dm

def do_dso_long_list(p, context):
    """
    This makes the very long list of DSOs.
    """
    location = context['location']

    targets = []
    all_dsos = DSO.objects.filter(
        dec__gt=context['dec_limit'], 
        magnitude__lt=context['mag_limit'],
        priority__in=['Highest', 'High']
    ).order_by('constellation__abbreviation')
    
    for dso in all_dsos:
        if dso.object_is_up(location, context['utdt_start'], min_alt=20.) \
                or dso.object_is_up(location, context['utdt_end'], min_alt=0.):
            targets.append(dso)
    n_lines = 0
    dx = 0
    y = 720
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, y, 'DSOs:')
    p.setFont('Helvetica', 7)
    y -= 30
    dy = y

    # Test
    for dso in targets:
        p.roundRect(30+dx, y, 7, 7, 2, stroke=1, fill=0)
        if dso.priority == 'Highest':
            p.setFont('Helvetica-Bold', 7)
        p.drawString(45+dx, y, dso.shown_name)
        if dso.priority == 'Highest':
            p.setFont('Helvetica', 7)
        p.drawString(90+dx, y, dso.constellation.abbreviation)
        p.drawString(120+dx, y, dso.object_type.code)
        p.drawString(150+dx, y, f"{dso.magnitude:4.1f}")
        p.drawString(170+dx, y, f"{dso.number_of_observations:2d}")
        y -= 11
        n_lines += 1
        if n_lines % 50 == 0 and n_lines != 0:
            dx += 190
            y = dy
        if n_lines == 150:
            p.showPage()
            y = 720
            p.setFont('Helvetica-Bold', 14)
            p.drawString(50, y, 'DSOs (cont.):')
            p.setFont('Helvetica', 7)
            y = dy
            dx = 0
    p.showPage()
    return p

def do_dso_lists(p, context, dso_lists=None):
    location = context['location']
    ut0 = context['utdt_start']    
    if dso_lists is None:
        dso_lists = DSOList.objects.filter(show_on_plan=1)
        
    for dl in dso_lists:
        # Are most of the things in the list going to be up during the session?
        ra = dl.mid_ra
        dec = dl.mid_dec
        up0 = is_object_up(ut0, location, ra, dec, min_alt=15.)[2]
        up1 = is_object_up(ut0, location, ra, dec, min_alt=15.)[2]
        #if not (up0 or up1):
        #    continue

        # Make the page for the DSO List
        y = Y0
        p, y = bold_text(p, X0, y, f'DSO List {dl.name}', size=18)

        # Set up map
        dso_set = dl.dso.all()
        center_ra, center_dec, max_dist, fov = get_map_parameters(dl.dso.all())
        star_mag_limit = get_star_mag_limit(max_dist)

        y = 760
        x = 350
        p, y = label_and_text(p, x, y, ('Center RA: ', 10), (to_hm(center_ra), 10))
        p, y = label_and_text(p, x, y, ('Center Dec: ', 10), (to_dm(center_dec), 10))
        y = 760
        x = 470
        p, y = label_and_text(p, x, y, ('FOV: ', 10), (f"{fov:.0f}°", 10))
        p, y = label_and_text(p, x, y, ('Mag. Limit: ', 10), (f"{star_mag_limit:.1f}", 10))

        map = plot_dso_list(
            center_ra, 
            center_dec, 
            dso_set, 
            reversed = False,
            fov = fov,
            star_mag_limit = star_mag_limit,
            label_size='small',
            symbol_size=60,
            title = f"DSO List: {dl.name}"
        )
        y = 735
        p, y = add_image(p, y, map, size=500, x=20)

        # Add table of member DSOs
        c = 0
        xoff = 0
        y -= 0
        ytop = y

        N_PER_COLUMN = 20
        for dso in dso_set:
            if c % N_PER_COLUMN == 0:
                p.setFont('Helvetica-Bold', 8)
                p.drawString(40+xoff, y, 'NAME')
                p.drawString(85+xoff, y, 'CON.')
                p.drawString(110+xoff, y, 'R.A.')
                p.drawString(155+xoff, y, 'DEC.')
                p.drawString(190+xoff, y, 'TYPE')
                p.drawString(215+xoff, y, 'MAG')
                p.drawString(240+xoff, y, 'LAST OBS.')
                y -= 15
                p.setFont('Helvetica', 7)
            p.drawString(40+xoff, y, dso.shown_name)
            p.drawString(85+xoff, y, dso.constellation.abbreviation)
            p.drawString(110+xoff, y, to_hm(dso.ra))
            p.drawString(155+xoff, y, to_dm(dso.dec))
            p.drawString(190+xoff, y, dso.object_type.code)
            if dso.magnitude is not None:
                p.drawString(215+xoff, y, f"{dso.magnitude:5.2f}")
            if dso.last_observed is not None:
                #p.setFont('Helvetica', 7)
                p.drawString(245+xoff, y, dso.last_observed.strftime('%Y-%m-%d'))
                #p.setFont('Helvetica', 8)
            y -= 10
            c += 1
            if c % N_PER_COLUMN == 0:
                xoff += 280
                y = ytop

        p.showPage()
    return p