from ...utils.format import to_sex, to_hm, to_dm, to_time

def show_object_table(obj, p, y, instance, xoff=0):
    app = obj['apparent']
    obs = obj['observe']
    p.drawString(50, y, obj['name'])
    p.drawString(120+xoff, y, 'in '+obs['constellation']['abbr'])
    p.drawString(150+xoff, y, to_hm(app['equ']['ra']))
    p.drawString(195+xoff, y, to_dm(app['equ']['dec']))
    p.drawString(230+xoff, y, f"{app['distance']['au']:5.2f}")
    p.drawString(260+xoff, y, f"{to_time(app['distance']['light_time'])}")
    p.drawString(300+xoff, y, f"{obs['apparent_magnitude']:5.2f}")
    if instance.last_observed is not None:
        p.drawString(330+xoff, y, instance.last_observed.strftime('%Y-%m-%d'))
    y -= 12
    return p, y

def show_table_header(p, y, xoff=0):
    p.setFont('Helvetica-Bold', 9)
    p.drawString(50, y, 'NAME')
    p.drawString(120+xoff, y, 'CON.')
    p.drawString(150+xoff, y, 'R.A.')
    p.drawString(195+xoff, y, 'DEC.')
    p.drawString(230+xoff, y, 'DIST')
    p.drawString(260+xoff, y, 'L.T.')
    p.drawString(300+xoff, y, 'MAG')
    p.drawString(330+xoff, y, 'LAST OBS.')
    y -= 15
    p.setFont('Helvetica', 8)
    return p, y

def do_line(p, x, y, l, dy=15):
    p.drawString(x, y, l)
    y -= dy
    return p, y