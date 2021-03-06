from ajax_select import LookupChannel
from django.urls import reverse


class BaseLookup(LookupChannel):
    """
    Base lookup class based on billing.managerers.LookupMixin
    """

    def get_query(self, q, request):
        return self.model.objects.lookup(q, request)

    def format_item_display(self, item):
        url = reverse(
            'admin:{}_{}_change'.format(item._meta.app_label,
                                        item._meta.model_name),
            args=[item.id])
        return '<a href="{}" target="_blank" class="ajax-select-link">{}</a>'.\
            format(url, item)
