from django.contrib import admin

# Из модуля models импортируем модель Category...
from .models import Birthday, Tag

# ...и регистрируем её в админке:
admin.site.register(Birthday) 
admin.site.register(Tag)