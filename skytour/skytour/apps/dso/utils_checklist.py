from django.db.models import Q

DSO_TYPE_DICT = {
    'cluster': ['asterism', 'cluster-nebulosity', 'globular-cluster', 
        'open-cluster', 'stellar-association'],
    'nebula': ['cluster-nebulosity', 'dark-nebula', 'diffuse-nebula', 'nebula--emission', 
        'interstellar-matter', 'planetary-nebula', 'reflection-nebula', 'supernova-remnant'],
    'galaxy': ['galaxy--barred-spiral', 'galaxy--cluster', 'galaxy--dwarf', 'galaxy--elliptical', 'galaxy--irregular',
        'galaxy--intermediate', 'galaxy--lenticular', 'galaxy--spiral', 'galaxy--unclassified']
}

def get_filter_params(request):
    params = dict(
        constellation = request.GET.get('constellation', None),
        subset = request.GET.get('subset', 'all'),
        imaged = request.GET.get('imaged', 'all'),
        priority = int(request.GET.get('priority', 0)),
        use_mode = request.GET.get('use_mode', None),
        dso_type = request.GET.get('dso_type', 'all'),
        ra_low = request.GET.get('ra_low', None),
        dec_low = request.GET.get('dec_low', None),
        ra_high = request.GET.get('ra_high', None),
        dec_high = request.GET.get('dec_high', None),
        redo_flag = request.GET.get('redo_flag', 'any')
    )
    return params

def filter_dsos(params, dsos):
    if params['constellation']:
        in_clist = [x.upper().strip() for x in params['constellation'].split(',')]
        dsos = dsos.filter(constellation__abbreviation__in=in_clist)

    if params['use_mode'] is not None: 
        use_mode = params['use_mode']
        use_pri = params['priority']

        if params['priority'] > 0:
            dsos = dsos.filter(dsoobservingmode__priority__gte=use_pri, dsoobservingmode__mode=use_mode)
        else:
            dsos = dsos.filter(dsoobservingmode__mode=use_mode).distinct()


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
    context['use_mode'] = params['use_mode'] if params['use_mode'] is not None else context['observing_mode']
    context['dec_low'] = params['dec_low']
    context['dec_high'] = params['dec_high']
    context['dso_type'] = params['dso_type']
    context['redo_flag'] = params['redo_flag']
    return context