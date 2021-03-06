from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from .models import Post
from django.db.models import Q, Count, Case, When
from comentarios.forms import FormComentario
from comentarios.models import Comentario
from django.contrib import messages
from django.db import connection
from django.views import View


class PostIndex(ListView):
    # ListView é usada para ver uma lista de objetos
    model = Post
    template_name = 'posts/index.html'
    paginate_by = 3
    context_object_name = 'posts'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('categoria_post')  
        # campo que tem a fk para categoria e com isso já melhora a performance
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

    '''
     -> essa função é apenas para mostrar no index através do {{ connection.queries|length }}, 
        quantas consultas são feitas para carregar aqueles poucos posts, que podem ser feitos
        com apenas 1 consulta.
     -> o que acontece é que por a categoria ser uma fk do post, ele precisa ir na tabela de categoria e seleciona
        o nome dessa categoria, causando entr 7 e 10 consultas para apenas 3 posts na página
     -> para combater isso utiliza o select_related() que melhora a performance, olhar os docs no site do django.
    '''
    '''
    def get_context_data(self, *, object_list=None, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['connection'] = connection

        return contexto
    '''


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


class PostDetalhes(View):
    template_name = 'posts/post_detalhes.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        pk = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=pk, publicado_post=True)
        self.contexto = {
            'post': post,
            'comentarios': Comentario.objects.filter(post_comentario=post, publicado_comentario=True),
            'form': FormComentario(request.POST or None),
        }
    
    def  get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.contexto)

    def post(self, request, *args, **kwargs):
        form = self.contexto['form']
        
        if not form.is_valid():
            return render(request, self.template_name, self.contexto)
        
        comentario = form.save(commit=False)  # salva, mas não armazena na base de dados

        if request.user.is_authenticated:
            comentario.usuario_comentario = request.user
            # armazena no usuário caso ele seja autenticado

        comentario.post_comentario = self.contexto['post']
        comentario.save()
        messages.success(request, 'Seu comentário foi enviado para revisão.')
        return redirect('post_detalhes', pk=self.kwargs.get('pk'))


'''
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

'''
    
