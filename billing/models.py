from django.conf import settings
from django.db import models


class CommonInfo(models.Model):
    """ CommonInfo abstract model """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_created_by")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        editable=False,
        related_name="%(app_label)s_%(class)s_modified_by")

    def __str__(self):
        return getattr(self, 'name', '{} #{}'.format(
            type(self).__name__, str(self.id)))

    class Meta:
        abstract = True
