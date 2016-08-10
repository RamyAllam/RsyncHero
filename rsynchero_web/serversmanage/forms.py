from django import forms
from . models import servers


class ServerAddForm(forms.ModelForm):
    hostname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    ip = forms.GenericIPAddressField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    sshport = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = servers
        fields = ['hostname', 'ip', 'sshport']


class ServerUpdateForm(forms.ModelForm):
    hostname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    ip = forms.GenericIPAddressField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    sshport = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = servers
        fields = ['hostname', 'ip', 'sshport']
