from django.shortcuts import render  # type: ignore[import-untyped]
from django.views.generic import TemplateView


# General views.
class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def custom_403_CSRF(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def custom_404(request, exception):
    return render(request, 'pages/404.html', status=404)


def custom_500(request):
    return render(request, 'pages/500.html', status=500)
