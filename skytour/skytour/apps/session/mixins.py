from django.http import HttpResponseRedirect
from .cookie import deal_with_cookie, get_all_cookies, test_all_cookies

class CookieMixin(object):

    def get_context_data(self, **kwargs):
        context = super(CookieMixin, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        context.update({'cookies': get_all_cookies(self.request)})
        return context

    def render_to_response(self, context):
        complete = test_all_cookies(context['cookies'])
        if not complete:
            return HttpResponseRedirect('/session/cookie')
        return super(CookieMixin, self).render_to_response(context)