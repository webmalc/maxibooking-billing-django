import adminactions.actions as actions
from django.contrib import admin
from django.contrib.admin import site
from django.utils.translation import ugettext_lazy as _

actions.add_to_site(site)


class TextFieldListFilter(admin.ChoicesFieldListFilter):
    template = "filters/text_field.html"

    def choices(self, changelist):
        yield {
            'selected':
            False,
            'query_string':
            changelist.get_query_string({
                self.lookup_kwarg: 0
            }, [self.lookup_kwarg_isnull]),
            'query_param':
            self.lookup_kwarg,
            'display':
            self.field
        }
