from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.models import AnonymousUser
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'core/index.html')

@login_required(login_url='login')
def panel(request):
    return render(request, 'core/panel.html')

class HomeSinPrevilegios(LoginRequiredMixin, TemplateView):
    template_name = 'core/sin_privilegios.html'
    login_url = 'login'


class SinPrivilegios(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = False
    redirect_field_name = "redirect_to"
    login_url = 'login'

    def handle_no_permission(self):
        if not self.request.user == AnonymousUser():
            self.login_url = 'sin_privilegios'
        return HttpResponseRedirect(reverse_lazy(self.login_url))


