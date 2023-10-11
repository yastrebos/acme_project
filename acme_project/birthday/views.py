# birthday/views.py 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import BirthdayForm
from .models import Birthday
# Импортируем из utils.py функцию для подсчёта дней.
from .utils import calculate_birthday_countdown


class BirthdayListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Birthday
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10


class BirthdayMixin:
    model = Birthday
    



class BirthdayCreateView(LoginRequiredMixin, BirthdayMixin, CreateView):
    form_class = BirthdayForm


class BirthdayUpdateView(LoginRequiredMixin, BirthdayMixin, UpdateView):
    form_class = BirthdayForm


class BirthdayDeleteView(LoginRequiredMixin, BirthdayMixin, DeleteView):
    pass 

class BirthdayDetailView(DetailView):
    model = Birthday 

    def get_context_data(self, **kwargs):
    # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        context['birthday_countdown'] = calculate_birthday_countdown(
            # Дату рождения берём из объекта в словаре context:
            self.object.birthday
        )
        # Возвращаем словарь контекста.
        return context 
    
@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')
