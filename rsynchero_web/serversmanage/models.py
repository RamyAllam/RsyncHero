from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
from vars import backuppaths_initial

# Validation function for valid paths
def validate_backuppaths(value):
    not_allowed_chars = ['$', '..', ')', '(', '()', '../', '&', ';', ' ', '\\']
    for not_allowed_chars_value in not_allowed_chars:
        if not_allowed_chars_value in value:
            raise ValidationError(('One of your paths is not valid,'
                                   ' Please make sure not to add any special characters except /'))


class servers(models.Model):
    hostname = models.CharField(max_length=1000)
    ip = models.GenericIPAddressField()
    serverstatus = models.CharField(max_length=10, default='Enabled')
    backupstatus = models.CharField(max_length=200, null=True)
    lastbackup = models.DateTimeField(null=True)
    sshport = models.IntegerField(default=22)
    backuppaths = models.TextField(default=backuppaths_initial, validators=[validate_backuppaths])

    def __str__(self):
        return self.ip

    def get_absolute_url(self):
        return reverse('serversmanage:serverinfo', kwargs={'pk': self.pk})
