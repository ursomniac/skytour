from ...dso.finder import plot_dso_list
from ...dso.helpers import get_map_parameters, get_star_mag_limit
from ...pdf.utils import bold_text, label_and_text, add_image
from ...pdf.utils import X0, Y0
from ...utils.format import to_hm, to_dm

def do_dso_lists(p, context, dso_lists=None):  
    if dso_lists is None:
        return p
        
    for dl in dso_lists:
        if dl.dso.count() == 0: ### Oops! empty list!
            return p

        # Make the page for the DSO List
        y = Y0
        p, y = bold_text(p, X0, y, f'DSO List {dl.name}', size=18)

        # Set up map
        dso_set = dl.dso.all()
        center_ra, center_dec, max_dist, fov = get_map_parameters(dso_set)
        star_mag_limit = get_star_mag_limit(max_dist)

        y = 770
        x = 460
        p, y = label_and_text(p, x, y, ('Center RA: ', 7), (to_hm(center_ra), 7), cr=9)
        p, y = label_and_text(p, x, y, ('Center Dec: ', 7), (to_dm(center_dec), 7), cr=9)
        p, y = label_and_text(p, x, y, ('FOV: ', 7), (f"{fov:.0f}°", 7), cr=9)
        p, y = label_and_text(p, x, y, ('Mag. Limit: ', 7), (f"{star_mag_limit:.1f}", 7), cr=9)

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