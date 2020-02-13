from django.db import models

class Categoria(models.Model):
    nome_cat = models.CharField(max_length=50)

    def __str__(self):
        return self.nome_cat
        # com isso vai aparecer o nome da categoria e não categoria_object