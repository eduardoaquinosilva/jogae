from django import forms 
from .models import Usuario
import re

class UsuarioForms(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username','email','password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if(3 > len(username)):
            raise forms.ValidationError("Nome de usuário precisa ter ao menos 3 caracteres")
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$', password):
            raise forms.ValidationError("A senha deve ter pelo menos 8 caracteres, com uma letra, um número e um caractere especial.")
        return password

class LoginForms(forms.Form):
    username = forms.CharField(label='Usuário', max_length=150)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, strip=False)