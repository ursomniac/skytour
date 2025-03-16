from .utils_avail import parse_utdt
    
class AvailableDSOMixin(object):
    """
    Mixin for the @Now and @Cookie view
    """
    def get_context_data(self, **kwargs):
        context = super(AvailableDSOMixin, self).get_context_data(**kwargs)

        def haz(thing):
            """
            Simple internal method to test for something being empty or None
            """
            if thing is None or thing == "None" or len(thing.strip()) == 0:
                return False
            return True

        # Deal with the form
        utdt_str = self.request.GET.get('utdt', None)
        utdt = parse_utdt(utdt_str)
        offset = self.request.GET.get('ut_offset', None)
        ut_offset = 0. if offset is None or (len(offset.strip()) == 0) else float(offset)
        # Set priority high so that the initial list isn't TOO big!
        priority = self.request.GET.get('min_priority', '3')
        min_priority = 3 if priority is None or (len(priority.strip()) == 0) else int(priority)
        imaged = self.request.GET.get('imaged', 'Redo')
        # These default to None if not set - the view will take care of putting in defaults
        min_dec = self.request.GET.get('min_dec', None)
        min_dec = None if not haz(min_dec) else float(min_dec)
        max_dec = self.request.GET.get('max_dec', None)
        max_dec = None if not haz(max_dec) else float(max_dec)
        alt0 = self.request.GET.get('min_alt', None)
        min_alt = None if not haz(alt0) else float(alt0)
        alt1 = self.request.GET.get('max_alt', None)
        max_alt = None if not haz(alt1) else float(alt1)

        raw_cookie = self.request.GET.get('cookie', None)
        is_now = raw_cookie is None

        if utdt:
            context['utdt'] = utdt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            context['utdt'] = None

        # Set the context to pass off to the DSOObjectsView
        context['ut_offset'] = ut_offset
        context['pri'] = priority
        context['imaged'] = imaged
        context['min_dec'] = min_dec
        context['max_dec'] = max_dec
        context['min_alt'] = min_alt
        context['max_alt'] = max_alt
        context['min_priority'] = min_priority
        context['is_now'] = is_now

        #print("SENDING CONTEXT BACK FROM DSO MIXIN: ", context.keys())
        return context