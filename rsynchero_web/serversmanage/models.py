from django.db import models
from django.core.urlresolvers import reverse


class servers(models.Model):
    hostname = models.CharField(max_length=1000)
    ip = models.GenericIPAddressField()
    serverstatus = models.CharField(max_length=10, default='Enabled')
    backupstatus = models.CharField(max_length=200, null=True)
    lastbackup = models.DateTimeField(null=True)
    sshport = models.IntegerField(default=22)

    def __str__(self):
        return self.ip

    def get_absolute_url(self):
        return reverse('serversmanage:serverinfo', kwargs={'pk': self.pk})
