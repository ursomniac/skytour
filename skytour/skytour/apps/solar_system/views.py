import datetime, pytz, time
from operator import itemgetter
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from ..abstract.utils import get_real_time_conditions
from ..abstract.vocabs import (
    IMAGE_CROPPING_OPTIONS, 
    IMAGE_ORIENTATION_CHOICES, 
    IMAGE_PROCESSING_STATUS_OPTIONS
)
from ..astro.almanac import get_twilight_begin_end
from ..astro.time import get_datetime_from_strings, convert_datetime_to_local_string
from ..session.cookie import deal_with_cookie
from ..session.mixins import CookieMixin
from ..tech.models import Telescope
from ..utils.timer import compile_times
from .asteroids import lookup_asteroid_object
from .comets import lookup_comet_by_name
from .forms import (
    TrackerForm, AsteroidEditForm, CometEditForm,
    PlanetObservationEditForm, AsteroidObservationEditForm, CometObservationEditForm,
    CometManagementForm, AsteroidManagementForm
)
from .helpers import compile_nearby_planet_list
from .models import (
    Comet, Planet, Asteroid, MeteorShower,
    CometLibraryImage, AsteroidLibraryImage, PlanetLibraryImage,
    CometObservation, AsteroidObservation, PlanetObservation, 
)
from .pdf import get_rise_set
from .planets import get_ecliptic_positions
from .plot import (
    create_finder_chart, 
    create_planet_system_view,
    plot_ecliptic_positions, 
    plot_track, 
    get_planet_map
)
from .utils import (
    get_constellation, 
    get_asteroid_from_cookie, 
    get_comet_from_cookie,
    get_planet_from_cookie,
    get_position_from_cookie,
    get_object_from_cookie,
    get_fov,
    get_mag_limit
)

class PlanetListView(CookieMixin, ListView):
    model = Planet 
    template_name = 'planet_list.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetListView, self).get_context_data(**kwargs)
        planets = Planet.objects.order_by('pk')
        planet_cookie = context['cookies']['planets']
        planet_list = []
        for p in planets:
            d = planet_cookie[p.name]
            d['n_obs'] = p.number_of_observations
            d['num_library_images'] = p.num_library_images
            d['last_observed'] = p.last_observed
            d['obj_rise'], d['obj_set'], d['obj_transit'] = get_rise_set(d['almanac'])
            planet_list.append(d)
        context['planet_list'] = planet_list

        moon = context['cookies']['moon']
        sun = context['cookies']['sun']
        context['moon_rise'], context['moon_set'], context['moon_transit'] = get_rise_set(moon['almanac'])
        context['sun_rise'], context['sun_set'], context['sun_transit'] = get_rise_set(sun['almanac'], format="%I:%M %p")
        
        twilight = context['cookies']['user_pref']['twilight']
        my_time_zone = pytz.timezone(context['location'].time_zone.pytz_name)
        twilight = get_twilight_begin_end(context['utdt_start'], context['location'], time_zone=my_time_zone)
        context['twilight'] = twilight
        print("Twilight: ", twilight)
        #context['twilight_begin'] = convert_datetime_to_local_string(twilight['begin'], location=context['location'])
        #context['twilight_end'] = convert_datetime_to_local_string(twilight['end'], location=context['location'])
        
        pdict = get_ecliptic_positions(context['utdt_start'])
        context['system_image'], context['ecl_pos'] = plot_ecliptic_positions(pdict, context['color_scheme'] == 'dark')
        return context

class PlanetDetailView(CookieMixin, DetailView):
    model = Planet
    template_name = 'planet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetDetailView, self).get_context_data(**kwargs)
            # Track performance
        times = [(time.perf_counter(), 'Start')]
        obj = self.get_object()
        planets_cookie = context['cookies']['planets']
        asteroids_cookie = context['cookies']['asteroids']
        
        flipped =  obj.name in ['Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'] and context['flip_planets'] == 'Yes'
        reversed = context['color_scheme'] == 'dark'

        utdt_start = context['utdt_start']
        pdict = context['planet'] = planets_cookie[obj.name]
        pdict['name'] = obj.name
        context['name'] = obj.name
        context['slug'] = obj.slug
        
        context['close_by'], times = compile_nearby_planet_list(obj.name, planets_cookie, utdt_start, times=times)
        times.append((time.perf_counter(), 'Got nearby planets'))
        fov = 2. if obj.name in ['Uranus', 'Neptune'] else 10.
        mag_limit = 10. if obj.name in ['Uranus', 'Neptune'] else 6.

        sun = context['cookies']['sun']
        moon = context['cookies']['moon']
        context['finder_chart'], times = create_finder_chart (
            utdt_start,
            obj, 
            planets_cookie,
            asteroids_cookie,
            reversed=reversed,
            mag_limit=mag_limit,
            flipped=False,
            fov=fov,
            sun=sun,
            moon=moon,
            show_dsos=False,
            times=times
        )

        context['view_image'], times = create_planet_system_view(
            utdt_start,
            obj, 
            planets_cookie,
            flipped=flipped,
            reversed=reversed,
            times=times
        )
        
        context['planet_map'] = None
        if obj.planet_map is not None: # Mars, Jupiter
            px, py, context['planet_map'] = get_planet_map(obj, pdict['physical'])
            context['xy'] = dict(px=px, py=py)
        slideshow = obj.image_library.order_by('order_in_list')
        context['library_slideshow'] = slideshow
        
        context['instance'] = obj
        context['times'] = compile_times(times)
        return context

class MoonDetailView(CookieMixin, TemplateView):
    template_name = 'planet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MoonDetailView, self).get_context_data(**kwargs)
        pdict = context['cookies']['moon']
        pdict['name'] = 'Moon'
        planets_cookie = context['cookies']['planets']
        asteroids_cookie = context['cookies']['asteroids']
        reversed = context['color_scheme'] == 'dark'
        context['planet'] = pdict
        context['name'] = 'Moon'
        context['slug'] = 'moon'

        context['moon_finder_chart'], ftimes = create_finder_chart (
            context['utdt_start'],
            pdict, 
            planets_cookie,
            asteroids_cookie,
            object_type = 'moon',
            obj_cookie = pdict,
            reversed = reversed,
            mag_limit = 6.5,
            fov = 15.
        )

        context['view_image'], _ = create_planet_system_view(
            context['utdt_start'],
            None,  # There is no Moon model instance
            pdict, # this is the moon cookie
            object_type = 'moon',
            flipped = False,
            reversed = reversed
        )
        return context 

class AsteroidListView(CookieMixin, ListView):
    model = Asteroid
    template_name = 'asteroid_list.html'

    def get_context_data(self, **kwargs):
        """
        TODO: Table should include rise/set based off of the cookie.
        """
        context = super(AsteroidListView, self).get_context_data(**kwargs)
        
        # TODO: allow full list of asteroids, but this might be time consuming
        all = self.request.GET.get('all', None) is not None
        asteroids = Asteroid.objects.order_by('number')
        if all:
            asteroid_list = asteroids
        else:
            asteroid_list = []
            asteroid_cookie = context['cookies']['asteroids']
            for d in asteroid_cookie:
                a = asteroids.get(number=d['number'])
                d['pk'] = a.pk
                d['cid'] = f"{d['number']:08d}"
                d['has_wiki'] = a.has_wiki
                d['n_obs'] = a.number_of_observations
                d['num_library_images'] = a.num_library_images
                d['last_observed'] = a.last_observed
                asteroid_list.append(d)
            asteroid_list = sorted(asteroid_list, key=itemgetter('cid'))
        context['asteroid_list'] = asteroid_list
        context['table_id'] = 'obs_asteroid_list'

        query = self.request.GET.get('query', None)
        if query:
            row = lookup_asteroid_object(query)
            context['result'] = row.to_frame().to_html()
            context['result_object'] = row
        return context

class AsteroidDetailView(CookieMixin, DetailView):
    model = Asteroid
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidDetailView, self).get_context_data(**kwargs)
        # Track performance
        times = [(time.perf_counter(), 'Start')]
        object = self.get_object()
        pdict = get_asteroid_from_cookie(context['cookies'], object)
        context['asteroid'] = pdict
        context['in_cookie'] = True if pdict else False
        slideshow = object.image_library.order_by('order_in_list')
        context['library_slideshow'] = slideshow
        context['times'] = compile_times(times)
        return context

class CometListView(CookieMixin, ListView):
    model = Comet
    template_name = 'comet_list.html'

    def get_context_data(self, **kwargs):
        """
        TODO: List should include rise/set info from the cookie.
        """
        context = super(CometListView, self).get_context_data(**kwargs)
        comets = Comet.objects.filter(status=1)
        # TODO: allow for full set of comets but this might be time consuming
        all = self.request.GET.get('all', None) is not None
        if all:
            comet_list = comets
        else:
            comet_list = []
            comet_cookie = context['cookies']['comets']
            for d in comet_cookie: # get the observation history for each comet on the list
                try:
                    comet = comets.get(pk=d['pk'])
                    d['mag_offset'] = comet.mag_offset
                    d['has_wiki'] = comet.has_wiki
                    d['n_obs'] = comet.number_of_observations
                    d['num_library_images'] = comet.num_library_images
                    d['last_observed'] = comet.last_observed
                    comet_list.append(d)
                except:
                    continue
        context['comet_list'] = comet_list
        context['table_id'] = 'obs_comet_list'
        return context

class CometDetailView(CookieMixin, DetailView):
    model = Comet
    template_name = 'comet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CometDetailView, self).get_context_data(**kwargs)
        # Track performance
        times = [(time.perf_counter(), 'Start')]
        object = self.get_object()
        comets = context['cookies']['comets']
        pdict = None
        for c in comets:
            if c['name'] == object.name:
                pdict = c
                pdict['n_obs'] = object.number_of_observations
                pdict['last_observed'] = object.last_observed
                mag = pdict['observe']['apparent_magnitude']
                pdict['mag_offset'] = object.mag_offset
                pdict['est_mag'] = mag + object.mag_offset
                break
        # TODO V2: if pdict is None then it's not in the cookie.
        # Figure out how to add things from that 
        context['comet'] = pdict
        #slideshow = object.image_library.filter(use_in_carousel=1).order_by('order_in_list')
        slideshow = object.image_library.order_by('order_in_list')
        context['library_slideshow'] = slideshow
        context['times'] = compile_times(times)
        return context

class TrackerView(FormView):
    """
    Combine planet, asteroid, and comet tracking into a single view.
    """
    form_class = TrackerForm
    template_name = 'tracker.html'
    success_url = '/solar_system/track'

    def get_form_kwargs(self):
        kwargs = super(TrackerView, self).get_form_kwargs()
        c = deal_with_cookie(self.request, {})
        alist = c.get('visible_asteroids', None)
        kwargs['asteroid_list'] = alist if alist is not None and len(alist) > 0 else None
        return kwargs

    def get_initial(self):
        initial = super(TrackerView, self).get_initial()
        c = deal_with_cookie(self.request, {})
        start_date = c.get('utdt_start', datetime.datetime.now(datetime.timezone.utc))
        end_date = start_date + datetime.timedelta(days=10)
        initial['start_date'] = start_date
        initial['end_date'] = end_date
        return initial

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        times = [(time.perf_counter(), 'Start')]

        context = deal_with_cookie(self.request, context)
        reversed = context['color_scheme'] == 'dark'
        d = form.cleaned_data
        model_dict = {'planet': Planet, 'asteroid': Asteroid, 'comet': Comet}
        object_type, slug = d['object'].split('--')
        if object_type not in model_dict.keys():
            context['issue'] = f'Object Type: {object_type} not found.'
            return context

        if object_type != 'comet':
            object = model_dict[object_type].objects.filter(slug=slug).first()
        else:
            object = Comet.objects.get(pk=slug)

        if not object:
            context['issue'] = f'{object_type} Object {slug} not found.'
            return context

        offset_before = 0
        offset_after = (d['end_date'] - d['start_date']).days
        step_days = d['date_step'] or 1
        step_labels = d['label_step'] or 5
        mag_limit = d['mag_limit'] or 8.
        fov = d['fov']
        dsos = d['show_dsos'] == '1'
        reversed = d['reversed'] == 'wob'
        x = d['start_date']
        utdt = datetime.datetime(x.year, x.month, x.day, 0, 0).replace(tzinfo=pytz.utc)

        context['track_image'], starting_position, track_positions, times = plot_track(
            utdt,
            object_type=object_type,
            object=object, 
            offset_before = offset_before,
            offset_after = offset_after,
            step_days = step_days,
            step_label = step_labels,
            mag_limit = mag_limit,
            fov=fov,
            reversed=reversed,
            return_data = True,
            dsos=dsos,
            times=times,
        )
        context['form'] = form
        context['track_positions'] = track_positions
        
        if starting_position:
            xra, xdec, xdist = starting_position.radec()
            context['observe'] = dict(
                ra = xra.hours.item(),
                dec = xdec.degrees.item(),
                dist =  xdist.au.item(),
                utdt = utdt
            )
            context['instance'] = object
            context['constellation'] = get_constellation(xra.hours.item(), xdec.degrees.item())
        context['times'] = compile_times(times)
        return self.render_to_response(context)

class TrackerResultView(TemplateView):
    template_name = 'tracker.html'

class OrreryView(TemplateView):
    template_name = 'orrery_view.html'

    def get_context_data(self, **kwargs):
        context = super(OrreryView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)        
        utdt = context['utdt_start']
        # Get the heliocentric ecliptic positions
        pdict = get_ecliptic_positions(utdt)
        context['system_image'], context['ecl_pos'] = plot_ecliptic_positions(pdict, reversed=False)
        return context

class PlanetRealTimeView(CookieMixin, DetailView):
    model = Planet
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetRealTimeView, self).get_context_data(**kwargs)
        cookie = None
        slug = self.kwargs['slug']
        object = self.get_object()
        context['object_type'] = 'Planet'
        context['object'] = object
        cookie = get_planet_from_cookie(context['cookies'], object)
        if cookie:
            object.ra_float, object.dec_float = get_position_from_cookie(cookie)
        context = get_real_time_conditions(object, self.request, context)
        return context
    
class MoonRealTimeView(CookieMixin, TemplateView):
    model = Planet
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(MoonRealTimeView, self).get_context_data(**kwargs)
        cookie = None
        slug = 'moon'
        object = None
        ra_float = None
        dec_float = None
        context['object_type'] = 'Moon'
        context['object'] = object
        cookie = context['cookies']['moon']
        if cookie:
            ra_float, dec_float = get_position_from_cookie(cookie)
            if object:
                object.ra_float = ra_float
                object.dec_float = dec_float
        context = get_real_time_conditions(
            object, 
            self.request, 
            context,
            ra_float = ra_float,
            dec_float = dec_float
        )
        return context
    
class AsteroidRealTimeView(CookieMixin, DetailView):
    model = Asteroid
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidRealTimeView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['object_type'] = 'Asteroid'
        context['object'] = object
        asteroid_cookie = get_asteroid_from_cookie(context['cookies'], object)
        # get ra and dec
        if asteroid_cookie:
            object.ra_float, object.dec_float = get_position_from_cookie(asteroid_cookie)
        context = get_real_time_conditions(object, self.request, context)
        return context
    
class CometRealTimeView(CookieMixin, DetailView):
    model = Comet
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(CometRealTimeView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['object_type'] = 'Comet'
        context['object'] = object
        comet_cookie = get_comet_from_cookie(context['cookies'], object)
        if comet_cookie:
            object.ra_float, object.dec_float = get_position_from_cookie(comet_cookie)
        context = get_real_time_conditions(object, self.request, context)
        return context
    
class SSOMapView(CookieMixin, TemplateView):
    template_name = 'sso_map_popup.html'

    def get_cookie_entry(object_type, object, cookie):
        if object_type == 'planet':
            return get_planet_from_cookie

    def get_context_data(self, **kwargs):
        context = super(SSOMapView, self).get_context_data(**kwargs)
        model = {'planet': Planet, 'asteroid': Asteroid, 'comet': Comet}
        object_type = self.kwargs['object_type']
        pk = self.kwargs['pk']
        style = self.kwargs['style'] # wide | narrow
        reversed = context['color_scheme'] == 'dark'

        object = model[object_type].objects.filter(pk=pk).first()
        pdict = get_object_from_cookie(object_type, context['cookies'], object)
        planets = context['cookies']['planets']
        asteroids = context['cookies']['asteroids']
        times = [(time.perf_counter(), 'Start Creating Map')]
        fov = get_fov(object_type, object, style)
        mag_limit = get_mag_limit(object_type, object, style)

        context['map'], times = create_finder_chart (
            context['utdt_start'],
            object,
            planets,
            asteroids,
            object_type = object_type,
            obj_cookie = pdict,
            fov = fov,
            reversed = reversed,
            mag_limit = mag_limit,
            sun = context['cookies']['sun'],
            moon = context['cookies']['moon'],
            show_dsos=False,
            times=times
        )
        context['title'] = f"{style.title()} for {object.name}"
        context['fov'] = fov
        context['mag_limit'] = mag_limit
        context['times'] = compile_times(times)
        return context
    
class SSOManageLibraryImagePanelView(TemplateView):
    template_name = 'manage_sso_library_image_panel.html'
    MODELS = {'planet': Planet, 'comet': Comet, 'asteroid': Asteroid}
    LIBRARY = {'planet': PlanetLibraryImage, 'comet': CometLibraryImage, 'asteroid': AsteroidLibraryImage}

    def post(self, request, *args, **kwargs):
        def haz(x): # All the ways something isn't something
            return x not in [None, 'None', '']
        def nodash(x):
            return x.replace('-','').strip() == 0

        object_type = self.kwargs['object_type']
        mymodel = self.MODELS[object_type]
        library = self.LIBRARY[object_type]
        sso = get_object_or_404(mymodel, pk=self.kwargs['pk'])

        if request.method == "POST":

            # how many existing images are there to process?
            num_items = request.POST.get('num_images', "0")

            # These are the simpler fields on the form for each image
            keys = ['pk', 'order', 'utdate', 'uttime','exptime', 'telescope', 'proc', 'orientation', 'crop']
            # create an index for every object in the form - including "extra"
            indexes = [str(x) for x in range(int(num_items))] + ['extra']

            # loop through every object on the form
            for n in indexes:
                op = None
                vals = {} # Store all the .get() values in here
                for k in keys: # do the easy ones first
                    name = f"form-{n}-{k}"
                    vals[k] = request.POST.get(name, None)
                # deal with the other fields
                vals['image'] = request.FILES.get(f"form-{n}-image", None)
                vals['delete'] = request.POST.get(f"form-{n}-delete", 'off') == 'on'

                # Toss things if not complete
                if n != 'extra' and vals['pk'] is None: # I needed a PK!
                    print("No PK found for updating image.")
                    continue

                # Get the DSOLibrary object or create one
                if n != 'extra': # This is an UPDATE - get the instance
                    img_object = library.objects.filter(pk=int(vals['pk'])).first()
                    if img_object is None: # didn't find it
                        print("Could not find image to update")
                        continue
                    # If this is a DELETE operation - do it now
                    if vals['delete']:
                        print("DELETEING image")
                        img_object.delete()
                        continue
                    op = 'UPDATE'

                else: # This is an INSERT operation - create a new instance!
                    img_object = library()
                    img_object.object_id = sso.pk  # set the parent DSO
                    op = 'CREATE'
                
                # OK - fill in the fields!
                img_object.use_as_map = 1
                img_object.use_in_carousel = 0

                # image order
                if haz(vals['order']):
                    order_val = int(vals['order'])
                else:
                    order_val = 0
                img_object.order_in_list = order_val

                # the image itself
                # If an image isn't added, skip it
                # This is the case if you DIDN'T add a new image, and only edited the other ones
                if vals['image'] is not None: 
                    img_object.image = vals['image']
                else:
                    if op == 'CREATE': # No image to upload
                        continue

                # deal with date/time (two fields on the form map to a datetime object)
                new_dt = get_datetime_from_strings(vals['utdate'], vals['uttime'])
                if new_dt is not None:
                    img_object.ut_datetime = new_dt

                # deal with exposure time (float)
                if haz(vals['exptime']):
                    exptime = float(vals['exptime'])
                    img_object.exposure = exptime

                # deal with Telescope FK
                if haz(vals['telescope']): # and nodash(vals['telescope']):
                    tel_id = int(vals['telescope'])
                    img_object.telescope_id = tel_id

                # the others are all strings... so they're straightforward
                if haz(vals['proc']): # and nodash(vals['proc']):
                    img_object.image_processing_status = vals['proc']
                if haz(vals['orientation']): # and nodash(vals['orientation']):
                    img_object.image_orientation = vals['orientation']
                if haz(vals['crop']): # and nodash(vals['crop']):
                    img_object.image_cropping = vals['crop']

                print("READY TO SAFE: ", vals)
                img_object.save()

        # Go back to the parent DSO Detail page with the updated panel!
        path = f"{object_type}-detail"
        if object_type == 'comet':
            return HttpResponseRedirect(reverse(path, kwargs={'pk': sso.pk}))
        return HttpResponseRedirect(reverse(path, kwargs={'slug': sso.slug}))


    def get_context_data(self, **kwargs):
        context = super(SSOManageLibraryImagePanelView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        object_type = self.kwargs['object_type']
        mymodel = self.MODELS[object_type]
        sso = get_object_or_404(mymodel, pk=pk)
        image_list = sso.image_library.order_by('order_in_list')
        context['sso'] = sso
        context['images'] = image_list
        context['num_images'] = image_list.count()
        context['extra'] = True
        context['telescopes'] = Telescope.objects.all()
        context['orientations'] = IMAGE_ORIENTATION_CHOICES
        context['croppings'] = IMAGE_CROPPING_OPTIONS
        context['procstats'] = IMAGE_PROCESSING_STATUS_OPTIONS
        return context
    
class AsteroidEditView(UpdateView):
    form_class = AsteroidEditForm
    model = Asteroid
    template_name = 'edit_asteroid.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Update successful')
        return response
    
    def get_success_url(self):
        referer = self.request.META.get('HTTP_REFERER')
        if referer: 
            return referer
        return reverse_lazy('asteroid-detail', kwargs={'slug': self.object.slug})

class CometEditView(UpdateView):
    form_class = CometEditForm
    model = Comet
    template_name = 'edit_comet.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Update successful')
        return response

    def get_success_url(self):
        referer = self.request.META.get('HTTP_REFERER')
        if referer: 
            return referer
        return reverse_lazy('comet-detail', kwargs={'pk': self.object.pk})
    
class PlanetObservationEditView(UpdateView):
    model = PlanetObservation
    form_class = PlanetObservationEditForm
    template_name = 'ssoobservation_edit.html'
    
    def get_success_url(self):
        object = self.object
        return reverse_lazy('session-detail', kwargs={'pk': object.session.pk})
    
    def get_context_data(self, **kwargs):
        context = super(PlanetObservationEditView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['parent'] = object.object
        return context
    
class AsteroidObservationEditView(UpdateView):
    model = AsteroidObservation
    form_class = AsteroidObservationEditForm
    template_name = 'ssoobservation_edit.html'
    
    def get_success_url(self):
        object = self.object
        return reverse_lazy('session-detail', kwargs={'pk': object.session.pk})
    
    def get_context_data(self, **kwargs):
        context = super(AsteroidObservationEditView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['parent'] = object.object
        return context
    
class CometObservationEditView(UpdateView):
    model = CometObservation
    form_class = CometObservationEditForm
    template_name = 'ssoobservation_edit.html'
    
    def get_success_url(self):
        object = self.object
        return reverse_lazy('session-detail', kwargs={'pk': object.session.pk})
    
    def get_context_data(self, **kwargs):
        context = super(CometObservationEditView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['parent'] = object.object
        return context
    
class CometManageListView(ListView):
    template_name = 'edit_comet_list.html'
    model = Comet

    def post(self, request, *args, **kwargs):
        form = CometManagementForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            existing = Comet.objects.filter(name=d['name']).first()
            if existing:
                # Comet found - don't add
                messages.error(request, "This comet is already in the Comet table.")
            else: 
                comet = lookup_comet_by_name(d['name'])
                if comet is not None:
                    obj = Comet()
                    obj.name = d['name']
                    obj.status = d['status']
                    obj.mag_offset = d['mag_offset']
                    obj.override_limts = d['override_limits']
                    obj.light_curve_url = d['light_curve_url']
                    obj.light_curve_graph_url = d['light_curve_graph_url']
                    obj.save()
                    return redirect('comet-list')
                else:
                    # Comet not found
                    messages.error(request, f"Object \"{d['name']}\" not in the MPC data file. <br>Check format/spacing.")
        # If we get here, then there are issues...
        self.object_list = self.get_queryset().order_by('-status', 'name')
        context = self.get_context_data()
        context['create_form'] = form # reset form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CometManageListView, self).get_context_data(**kwargs)
        context['object_list'] = self.get_queryset().order_by('-status', 'name')
        context['create_form'] = CometManagementForm()
        context['table_id'] = 'all-comet-list'
        return context

class AsteroidManageListView(ListView):
    template_name = 'edit_asteroid_list.html'
    model = Asteroid

    def post(self, request, *args, **kwargs):
        form = AsteroidManagementForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            existing = Asteroid.objects.filter(number=d['number']).first()
            if existing is not None:
                #print("ERROR: object in DB")
                messages.error(request, "This asteroid is already in the Asteroid table.")
            else:
                name = f"({d['number']}) {d['name']}"
                #print(f"Looking up: \'{name}\'")
                mpc = lookup_asteroid_object(name)
                if mpc is None:
                    #print("Did not find it.")
                    messages.error(request, f"Asteroid \"{name}\" not in the MPC data file. <br>Check format/spacing.")
                else:
                    obj = Asteroid()
                    obj.pk = d['number']
                    obj.mpc_json = mpc.to_json()
                    obj.number = d['number']
                    obj.name = d['name']
                    obj.diameter = d['diameter']
                    obj.year_of_discovery = d['year_of_discovery']
                    obj.image = request.FILES.get("image", None)
                    obj.classification = d['classification']
                    obj.description = d['description']
                    obj.always_include = d['always_include']
                    try:
                        obj.save()
                        messages.success(request, f"Asteroid {name} successfully added.")
                    except:
                        #print("ERROR in save()", obj)
                        messages.error(request, f"Error saving Asteroid {name}.")
                    return redirect('asteroid-edit-list')
                
        self.object_list = self.get_queryset().order_by('number', 'name')
        context = self.get_context_data()
        context['create_form'] = form # reset form
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AsteroidManageListView, self).get_context_data(**kwargs)
        context['object_list'] = self.get_queryset().order_by('pk')
        context['create_form'] = AsteroidManagementForm()
        context['table_id'] = 'all-asteroid-list'
        return context

class AsteroidWikiPopup(DetailView):
    model = Asteroid
    template_name = 'wiki_content.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidWikiPopup, self).get_context_data(**kwargs)
        asteroid = self.get_object()
        text = asteroid.wiki.summary
        html_output = "".join(f"<p>{line.strip()}</p>\n" for line in text.strip().splitlines())
        context['object'] = asteroid
        context['text'] = html_output
        return context
    
class PlanetWikiPopup(DetailView):
    model = Planet
    template_name = 'wiki_content.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetWikiPopup, self).get_context_data(**kwargs)
        planet = self.get_object()
        text = planet.wiki.summary
        html_output = "".join(f"<p>{line.strip()}</p>\n" for line in text.strip().splitlines())
        context['object'] = planet
        context['text'] = html_output
        return context
    
class CometWikiPopup(DetailView):
    model = Comet
    template_name = 'wiki_content.html'

    def get_context_data(self, **kwargs):
        context = super(CometWikiPopup, self).get_context_data(**kwargs)
        comet = self.get_object()
        text = comet.wiki.summary
        html_output = "".join(f"<p>{line.strip()}</p>\n" for line in text.strip().splitlines())
        context['object'] = comet
        context['text'] = html_output
        return context
    
class MeteorShowerListView(ListView):
    model = MeteorShower
    template_name = 'meteor_list.html'
    
    def get_context_data(self, **kwargs):
        context = super(MeteorShowerListView, self).get_context_data(**kwargs)
        context['table_id'] = 'meteor-list'
        return context

class MeteorShowerDetailView(DetailView):
    model = MeteorShower
    template_name = 'meteor_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MeteorShowerDetailView, self).get_context_data(**kwargs)
        return context

class MeteorShowerWikiPopup(DetailView):
    model = MeteorShower
    template_name = 'wiki_content.html'

    def get_context_data(self, **kwargs):
        context = super(MeteorShowerWikiPopup, self).get_context_data(**kwargs)
        shower = self.get_object()
        text = shower.wiki.summary
        html_output = "".join(f"<p>{line.strip()}</p>\n" for line in text.strip().splitlines())
        context['text'] = html_output
        return context