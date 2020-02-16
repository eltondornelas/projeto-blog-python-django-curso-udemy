from django.forms import ModelForm
from .models import Comentario
import requests


class FormComentario(ModelForm):

    def clean(self):
        # validando o captcha primeiro
        raw_data = self.data
        recaptcha_response = raw_data.get('g-recaptcha-response')

        ''' essa validação não tem mais sentido, pois a debaixo faz essa validação com a chave também
        if not recaptcha_response:
            self.add_error(
                'comentario', 'Por favor, marque a caixa "Não sou um robô".'
            )
        '''
        
        # https://google.com/recaptcha/api/siteverify
        # secret_key
        # resposta_captcha

        recaptcha_request = requests.post(
            'https://google.com/recaptcha/api/siteverify',
            data={
                'secret': '6LfhYtkUAAAAAGvSkHCzmYaVHcK357qLhTgbR-eW',  # secret_key do backend
                'response': recaptcha_response
            }
        )
        
        recaptcha_result = recaptcha_request.json()

        if not recaptcha_result.get('success'):
            self.add_error(
                'comentario', 'Ocorreu um erro.'
            )
        
        # print(recaptcha_result)

        # o clean coloca as validações para aparecer as msgs de erro no seu devido campo, precisa pegar os dados primeiro
        cleaned_data = self.cleaned_data
        # print(data)
        nome = cleaned_data.get('nome_comentario')
        email = cleaned_data.get('email_comentario')
        comentario = cleaned_data.get('comentario')

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