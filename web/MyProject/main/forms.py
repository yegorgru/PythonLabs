from django import forms


class UserForm(forms.Form):
    unit_id = forms.IntegerField()