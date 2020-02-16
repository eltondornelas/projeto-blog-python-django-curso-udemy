from django.forms import ModelForm
from .models import Comentario


class FormComentario(ModelForm):

    def clean(self):
        # o clean coloca as validações para aparecer as msgs de erro no seu devido campo, precisa pegar os dados primeiro
        data = self.cleaned_data
        # print(data)
        nome = data.get('nome_comentario')
        email = data.get('email_comentario')
        comentario = data.get('comentario')

        if len(nome) < 5:
            self.add_error(
                'nome_comentario', 'Nome precisa ter mais que 5 caracteres.'
            )        

        '''if not email:
            self.add_error(
                'email_comentario', 'erro no email.'
            )'''
            
        

    class Meta:
        # campos que quero no comentario
        model = Comentario
        fields = ('nome_comentario', 'email_comentario', 'comentario')