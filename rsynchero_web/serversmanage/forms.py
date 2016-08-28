from django import forms
from . models import servers
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
from vars import backuppaths_initial


class ServerAddForm(forms.ModelForm):
    hostname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial='server.xyz.com')
    ip = forms.GenericIPAddressField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial='192.168.1.50')
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial='root')
    sshport = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial=22)
    backuppaths = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), initial=backuppaths_initial)

    class Meta:
        model = servers
        fields = ['hostname', 'ip', 'username', 'sshport', 'backuppaths']


class ServerUpdateForm(forms.ModelForm):
    hostname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    ip = forms.GenericIPAddressField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    sshport = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    backuppaths = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = servers
        fields = ['hostname', 'ip', 'username', 'sshport', 'backuppaths']
