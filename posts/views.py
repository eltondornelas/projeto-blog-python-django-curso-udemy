from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from .models import Post
from django.db.models import Q, Count, Case, When
from comentarios.forms import FormComentario
from comentarios.models import Comentario
from django.contrib import messages


class PostIndex(ListView):
    model = Post
    template_name = 'posts/index.html'
    paginate_by = 3
    context_object_name = 'posts'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.order_by('-id').filter(publicado_post=True)

        # anotação SQL
        qs = qs.annotate(
            numero_comentarios=Count(
                Case(
                    When(comentario__publicado_comentario=True, then=1)
                )
            )
        )
        
        return qs


class PostBusca(PostIndex):
    template_name = 'posts/post_busca.html'

    # sobreescreve o método do index
    def get_queryset(self):
        qs = super().get_queryset()
        # print(self.request.GET.get('termo'))
        termo = self.request.GET.get('termo')

        if not termo:
            return qs

        qs = qs.filter(
            Q(titulo_post__icontains=termo) |
            Q(autor_post__first_name__iexact=termo) |            
            Q(conteudo_post__icontains=termo) |
            Q(excerto_post__icontains=termo) |
            Q(categoria_post__nome_cat__iexact=termo)
        )

        return qs


class PostCategoria(PostIndex):
    template_name = 'posts/post_categoria.html'

    # sobreescreve o método do index
    def get_queryset(self):
        qs = super().get_queryset()        
        
        # print(self.kwargs.get('categoria', None))
        # print(self.kwargs.get())
        categoria = self.kwargs.get('categoria', None)
        # verificando se há algum post do tipo categoria

        if not categoria:
            return qs

        qs = qs.filter(categoria_post__nome_cat__iexact=categoria)
        # filtrando as categorias para que só mostra aquela categoria na página
        # lembrando que categoria_post é uma ForeignKey
        # nomeCampoModel__nomeCampoDaForeignKey__tipoDePesquisa=valorDaBusca
        # o "i" de iexact quer dizer que é case insensitive e o exact é como se fosse igual

        return qs


class PostDetalhes(UpdateView):
    # UpdateView espera um formulário porém, vamos usar o form de comentario
    template_name = 'posts/post_detalhes.html'
    model = Post
    form_class = FormComentario
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        post = self.get_object()
        # obtendo o post do momento
        comentarios = Comentario.objects.filter(publicado_comentario=True, post_comentario=post.id)        
        # filtrando da base de dados
        
        contexto['comentarios'] = comentarios

        return contexto

    def form_valid(self, form):
        post = self.get_object()
        # pega o post que está
        comentario = Comentario(**form.cleaned_data)
        # ** = extraido ??
        comentario.post_comentario = post

        if self.request.user.is_authenticated:
            # se for um usuário logado quero que o campo de usuário seja preenchido pelo nome do usuário logado
            comentario.usuario_comentario = self.request.user

        comentario.save()

        messages.success(self.request, 'Comentário enviado com sucesso.')
        
        return redirect('post_detalhes', pk=post.id)



    
