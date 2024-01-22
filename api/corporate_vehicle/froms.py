from django import forms
from api.models import CorporateMgmt


class CorporateMgmtForm(forms.ModelForm):
    class Meta:
        model = CorporateMgmt
        fields = ['oiling', 'distance', 'maintenance', 'etc', 'event_mgm']
