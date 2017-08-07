from django.db import models
from django.db.models import Sum


class PropertyManager(models.Manager):
    """"
    Property manager
    """

    def count_rooms(self, client):
        """
        Count client property rooms
        """

        return self.filter(client=client).aggregate(Sum('rooms'))['rooms__sum']
