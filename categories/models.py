from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name='Назва категорії')
    color = models.CharField(max_length=7, default='#000000', verbose_name='Колір (HEX)')

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
