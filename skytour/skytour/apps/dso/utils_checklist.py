from django.db.models import Q
from .models import DSOList

DSO_TYPE_DICT = {
    'cluster': ['asterism', 'cluster-nebulosity', 'globular-cluster', 
        'open-cluster', 'stellar-association'],
    'nebula': ['cluster-nebulosity', 'dark-nebula', 'diffuse-nebula', 'nebula--emission', 
        'interstellar-matter', 'planetary-nebula', 'reflection-nebula', 'supernova-remnant'],
    'galaxy': ['galaxy--barred-spiral', 'galaxy--cluster', 'galaxy--dwarf', 'galaxy--elliptical', 'galaxy--irregular',
        'galaxy--intermediate', 'galaxy--lenticular', 'galaxy--spiral', 'galaxy--unclassified']
}

def checklist_params(request):
    params = dict(
        constellation = request.GET.get('constellation', None),
        #seen = request.GET.get('seen', False) == 'on',
        subset = request.GET.get('subset', 'all'),
        priority = int(request.GET.get('priority', 0)),
        dso_type = request.GET.get('dso_type', 'all'),
        exclude_issues = request.GET.getlist('exclude_issues', None),
        create_list = request.GET.get('create_list', False) == 'on',
        new_list_name = request.GET.get('new_list_name', None),
        show_map = request.GET.get('show_map', False) == 'on'
    )
    return params

def checklist_form(params, dsos):
    # constellation
    if params['constellation']:
        in_clist = [x.upper().strip() for x in params['constellation'].split(',')]
        dsos = dsos.filter(dso__constellation__abbreviation__in=in_clist)
    if params['priority'] > 0:
        dsos = dsos.filter(priority__gte=(params['priority'] -1))
    if params['dso_type'] != 'all':
        in_list = DSO_TYPE_DICT[params['dso_type']]
        dsos = dsos.filter(dso__object_type__slug__in=in_list)

    if params['subset'] == 'seen':
        good_ids = [x.pk if x.dso.num_library_images > 0 else None for x in dsos]
        dsos = dsos.filter(pk__in=good_ids)
    elif params['subset'] == 'unseen':
        good_ids = [x.pk if x.dso.num_library_images == 0 else None for x in dsos]
        dsos = dsos.filter(pk__in=good_ids)

    for issue in params['exclude_issues']:
        #print("ISSUE: ", issue)
        if issue == 'all':
            continue
        dsos = dsos.exclude(issues=issue)
        
    return dsos

def create_new_observing_list(imaging_list, params):
    name = params['new_list_name']
    description = f"""
        Constellations: {params['constellation']}
        Exclude: {params['exclude_issues']}
        Imaging: {params['subset']}
        Object Types: {params['dso_type']}
        Priority: {params['priority']}
    """
    new_list = DSOList()
    new_list.name = name
    new_list.description = description
    new_list.save() # need to do this before adding DSOs
    for item in imaging_list:
        new_list.dso.add(item.dso)
    new_list.save()
    return new_list

def get_filter_params(request):
    params = dict(
        constellation = request.GET.get('constellation', None),
        subset = request.GET.get('subset', 'all'),
        imaged = request.GET.get('imaged', 'all'),
        priority = int(request.GET.get('priority', 0)),
        dso_type = request.GET.get('dso_type', 'all'),
        ra_low = request.GET.get('ra_low', None),
        dec_low = request.GET.get('dec_low', None),
        ra_high = request.GET.get('ra_high', None),
        dec_high = request.GET.get('dec_high', None),
        imaging_priority = int(request.GET.get('imaging_priority', 0)),
        redo_flag = request.GET.get('redo_flag', 'any')
    )
    return params

def filter_dsos(params, dsos):
    if params['constellation']:
        in_clist = [x.upper().strip() for x in params['constellation'].split(',')]
        dsos = dsos.filter(constellation__abbreviation__in=in_clist)

    if params['priority'] > 0:
        use = params['priority']
        good_ids = [x.pk for x in dsos if x.priority_value >= use]
        dsos = dsos.filter(pk__in=good_ids)

    if params['imaging_priority'] > 0:
        use = params['imaging_priority']
        good_ids = []
        for x in dsos:
            if x.dsoimagingchecklist_set.count() > 0:
                ip = x.dsoimagingchecklist_set.first().priority
                if ip >= use:
                    good_ids.append(x.pk)
        dsos = dsos.filter(pk__in=good_ids)

    if params['redo_flag'] != 'any':
        use = params['redo_flag'] == 'yes'
        good_ids = [x.pk for x in dsos if x.reimage == use]
        dsos = dsos.filter(pk__in=good_ids)

    if params['dso_type'] != 'all':
        in_list = DSO_TYPE_DICT[params['dso_type']]
        dsos = dsos.filter(object_type__slug__in=in_list)

    if params['subset'] == 'observed':
        good_ids = [x.pk for x in dsos if x.number_of_observations > 0]
        dsos = dsos.filter(pk__in=good_ids)
    elif params['subset'] == 'unobserved':
        good_ids = [x.pk for x in dsos if x.number_of_observations == 0]
        dsos = dsos.filter(pk__in=good_ids)

    if params['imaged'] == 'imaged':
        good_ids = [x.pk for x in dsos if x.num_library_images > 0]
        dsos = dsos.filter(pk__in=good_ids)
    elif params['imaged'] == 'unimaged':
        good_ids = [x.pk for x in dsos if x.num_library_images == 0]
        dsos = dsos.filter(pk__in=good_ids)

    if params['ra_low'] and params['ra_high']:
        if params['ra_low'] < params['ra_high']:
            dsos = dsos.filter(ra__gte=params['ra_low'], ra__lte=params['ra_high'])
        else: # crosses 0h!
            dsos = dsos.filter(Q(ra__gte=params['ra_low']) | Q(ra__lte=params['ra_high']))
    if params['dec_low'] and params['dec_high']:
        dsos = dsos.filter(dec__gte=params['dec_low'], dec__lte=params['dec_high'])
    
    return dsos

def update_dso_filter_context(context, params):
    context['constellation'] = params['constellation']
    context['subset'] = params['subset']
    context['imaged'] = params['imaged']
    context['ra_low'] = params['ra_low']
    context['ra_high'] = params['ra_high']
    context['priority'] = params['priority']
    context['dec_low'] = params['dec_low']
    context['dec_high'] = params['dec_high']
    context['dso_type'] = params['dso_type']
    context['redo_flag'] = params['redo_flag']
    context['imaging_priority'] = params['imaging_priority']
    return context