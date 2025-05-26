from django.shortcuts import render, redirect
from .forms import UsuarioForms

# Create your views here.

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