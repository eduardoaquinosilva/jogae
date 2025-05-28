from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from .forms import UsuarioForms, LoginForms

# Create your views here.
def login_view(request):
    if(request.method == 'POST'):
        form = LoginForms(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Usuário ou senha inválidos.')
    else:
        form = LoginForms()
    return render(request, 'usuarios/login.html', {'form': form})

def registrar_usuario(request):


    if(request.method == 'POST'):
        form = UsuarioForms(request.POST)

        if form.is_valid():
            form.save()
            return redirect('pagina_sucesso')
    else:
        form = UsuarioForms()
    return render(request, 'usuarios/formulario.html', {'form': form})

def pagina_sucesso(request):
    return render(request, 'usuarios/sucesso.html')