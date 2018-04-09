import adminactions.actions as actions
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.postgres.fields import JSONField
from prettyjson import PrettyJSONWidget

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


class JsonAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {
            'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})
        }
    }


class DictAdminMixin():
    """
    DictAdminMixin admin interface
    """

    list_display_links = ['id', 'title']
    list_select_related = [
        'modified_by',
    ]
    search_fields = ['=pk', 'title', 'description']
    readonly_fields = [
        'code', 'created', 'modified', 'created_by', 'modified_by'
    ]
    actions = None

    def get_fieldsets(self, request, obj=None):
        return [
            ['General', {
                'fields': ['title', 'description']
            }],
            [
                'Options', {
                    'fields': [
                        'is_enabled', 'code', 'created', 'modified',
                        'created_by', 'modified_by'
                    ]
                }
            ],
        ]

    def get_list_display(self, request):
        return ['id', 'title', 'code', 'is_enabled', 'modified', 'modified_by']

    def has_delete_permission(self, request, obj=None):
        parent = super().has_delete_permission(request, obj)
        if parent and obj and obj.code:
            return False
        return parent
