from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    name = forms.CharField(label=_('Nombre'), max_length=100,
        widget=forms.TextInput(attrs={'class' :'form-control'}))

    phone = forms.CharField(label=_('Teléfono'), max_length=20,
        widget=forms.TextInput(attrs={'class' :'form-control'}),
        help_text=_('10 dígitos. Teléfono con lada.'))

    email = forms.EmailField(label=_('Email'), required=False,
        widget=forms.EmailInput(attrs={'class' :'form-control'}))

    message = forms.CharField(label=_('Mensaje'), 
        widget=forms.Textarea(attrs={'class':'form-control', 'rows': '5'}))

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        phone = [x for x in phone if x.isdigit()]
        num_digits = len(phone)
        
        if num_digits < 10:
            self.add_error(
                'phone', _('Mínimo 10 dígitos. Indica tu teléfono con lada.'))
        
        if num_digits > 15:
            self.add_error(
                'phone', _('Máximo 15 dígitos. Indica tu teléfono con lada.'))
        
        return ''.join(phone)