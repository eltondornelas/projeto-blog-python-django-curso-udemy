from django import template


register = template.Library()
# register vai decorar as funções

@register.filter(name='plural_comentarios')  # não é obrigatório colocar o "name"
def plural_comentarios(num_comentarios):
    # esse retorno é o que irá mostrar no template em index em {{ post.numero_comentarios }}
    try:
        num_comentarios = int(num_comentarios)
        
        if num_comentarios == 0:
            return f'Nenhum comentário'
        elif num_comentarios == 1:
            return f'{num_comentarios} comentário'
        else:
            return f'{num_comentarios} comentários'
    except:        
        return f'{num_comentarios} comentário(s)'
