from ajax_select import register, LookupChannel
from .models import DSO

@register('dso')
class DSOLookup(LookupChannel):
    model = DSO

    def get_query(self, q, request):
        return self.model.objects.filter(shown_name__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item.shown_name

        