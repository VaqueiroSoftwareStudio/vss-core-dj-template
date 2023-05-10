from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, TemplateView

from vss.apps.core.captcha import CaptchaMixin
from vss.apps.data.models import SiteBrandingData, SiteContactData

from .forms import ContactForm


class FormInvalidMixin(FormView):

    def form_invalid(self, form):
        for field in form.errors:
            if field in form.fields:
                base_class = form[field].field.widget.attrs.get('class', '')
                form[field].field.widget.attrs[
                    'class'] = base_class + ' is-invalid'
        return super().form_invalid(form)


@method_decorator(cache_page(86400), name='dispatch')
class IndexView(TemplateView):
    template_name = 'index.html'


@method_decorator(cache_page(86400), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class ContactView(CaptchaMixin, FormInvalidMixin):
    form_class = ContactForm
    template_name = 'contact_form.html'
    success_url = reverse_lazy('vss_landing_contact')

    def send_contact_email(self, cleaned_data):
        
        site = get_current_site(self.request)

        contact_data = SiteContactData.objects.get(site=site)
        branding_data = SiteBrandingData.objects.get(site=site)

        context = {
            'form_data' : cleaned_data,
            'contact_data' : contact_data,
            'branding' : branding_data,
            'protocol' : 'https' if self.request.is_secure() else 'http',
            'domain': site.domain,
            'request' : self.request,
            'site' : site,
        }

        subject = _(f'[{site.name}] Nuevo mensaje de contacto.')

        context.update({'email_subject':subject})

        body_html = render_to_string(
            'contact_email.html', context=context)
        
        body_plain = strip_tags(body_html)

        admin_emails = self.get_admin_emails(contact_data)

        if admin_emails:

            send_mail(subject, body_plain, settings.DEFAULT_FROM_EMAIL,
                admin_emails, html_message=body_html, fail_silently=False)
    

    def get_admin_emails(self, data=None):
        if data and data.admin_email:
            return [data.admin_email,]
        return []

    def form_valid(self, form):
        
        if self.is_captcha_valid():
            ctx = form.cleaned_data
            self.send_contact_email(ctx)
            messages.success(self.request,
            _('¡Mensaje enviado! Gracias por ponerte en contacto con nostros.'))
            return HttpResponseRedirect(self.get_success_url())
        else:
            form.add_error('', _('reCaptcha Inválido.'))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request,
            _('¡Error en formulario! Completa todos los campos correctamente.'))
        return super().form_invalid(form)