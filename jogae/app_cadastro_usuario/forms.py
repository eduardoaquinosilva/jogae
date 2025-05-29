from django import forms 
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
import re

User = get_user_model()

class UsuarioForms(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if(username and 3 > len(username)):
            raise forms.ValidationError("Nome de usuário precisa ter ao menos 3 caracteres")
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$', password):
            raise forms.ValidationError("A senha deve ter pelo menos 8 caracteres, com uma letra, um número e um caractere especial.")
        return password