from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import User
from .forms import UsuarioForms

class SignUpView(CreateView):
    form_class = UsuarioForms
    template_name = 'registration/cadastro.html'
    success_url = reverse_lazy('games:index') # TODO: redirecionar para perfil / última página visitada

    # This will be called when valid form data has been posted
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)