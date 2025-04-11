from django.db.models import Q

DSO_TYPE_DICT = {
    'cluster': [
        'asterism', 'cluster-nebulosity', 'globular-cluster', 
        'open-cluster', 'stellar-association'
    ],
    'cluster--open': [
        'open-cluster', 'stellar-association', 'cluster-nebulosity', 'asterism'
    ],
    'cluster--globular': ['globular-cluster'],
    'nebula': [
        'cluster-nebulosity', 'dark-nebula', 'diffuse-nebula', 'nebula--emission', 
        'interstellar-matter', 'planetary-nebula', 'reflection-nebula', 'supernova-remnant'
    ],
    'nebula--emission': [
        'cluster-nebulosity', 'diffuse-nebula', 'nebula--emission', 'interstellar-matter'
    ],
    'nebula--dark': ['dark-nebula'],
    'nebula--reflection': ['reflection-nebula'],
    'nebula--planetary': ['planetary-nebula', 'supernova-remnant'],
    'galaxy': [
        'galaxy--barred-spiral', 'galaxy--cluster', 'galaxy--dwarf', 'galaxy--elliptical', 
        'galaxy--irregular', 'galaxy--intermediate', 'galaxy--lenticular', 'galaxy--spiral', 
        'galaxy--unclassified', 'galaxy--compact-group'
    ],
    'galaxy--spiral': [ 
        'galaxy--barred-spiral', 'galaxy--dwarf', 'galaxy--intermediate',  'galaxy--spiral'
    ],
    'galaxy--elliptical': ['galaxy--lenticular',  'galaxy--elliptical' ],
    'galaxy--group': ['galaxy--cluster', 'galaxy--compact-group' ],
    'other': [ 'quasar', 'black-hole-system']
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
        size_min = request.GET.get('size_min', None),
        mag_max = request.GET.get('mag_max', None),
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
    
    if params['mag_max']:
        mag_max = float(params['mag_max'])
        good_pks = [
            x.pk for x in dsos 
            if (x.find_magnitude[0] is None or x.find_magnitude[0] <= mag_max)
        ]
        dsos = dsos.filter(pk__in=good_pks)

    if params['size_min']:
        size_min = float(params['size_min'])
        good_pks = [
            x.pk for x in dsos
            if (x.find_major_axis_size[0] is None 
                or x.find_major_axis_size[0] >= size_min)
        ]
        dsos = dsos.filter(pk__in=good_pks)

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
    context['size_min'] = params['size_min']
    context['mag_max'] = params['mag_max']
    return context