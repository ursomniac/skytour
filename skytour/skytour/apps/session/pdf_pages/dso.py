from ...dso.models import DSO, DSOList

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
            #priority = dso.priority.lower()
            #if priority in targets.keys():
            #    targets[priority].append(dso)
            #else:
            #    targets[priority] = [dso]
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