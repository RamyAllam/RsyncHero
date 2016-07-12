from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from . models import servers
from django.core.urlresolvers import reverse_lazy


class IndexView(generic.ListView):
    template_name = 'serversmanage/index.html'

    def get_queryset(self):
        return servers.objects.all()


class ServerInfo(generic.DetailView):
    model = servers
    template_name = 'serversmanage/serverinfo.html'


class ServerAdd(CreateView):
    model = servers
    fields = ['hostname', 'ip', 'sshport']
    template_name = 'serversmanage/server_form.html'


class ServerUpdate(UpdateView):
    model = servers
    fields = ['hostname', 'ip', 'sshport', 'serverstatus']
    template_name = 'serversmanage/server_form.html'


class ServerDelete(DeleteView):
    model = servers
    # Return to the index vide in the url.py file after deleting
    success_url = reverse_lazy('serversmanage:index')
