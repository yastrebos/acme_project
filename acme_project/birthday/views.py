# birthday/views.py 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.shortcuts import get_object_or_404, redirect
from .forms import CongratulationForm

from .forms import BirthdayForm, CongratulationForm
from .models import Birthday, Congratulation
# Импортируем из utils.py функцию для подсчёта дней.
from .utils import calculate_birthday_countdown
from django.urls import reverse


class BirthdayListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Birthday
    queryset = Birthday.objects.prefetch_related(
        'tags'
    ).select_related('author')
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10


class BirthdayMixin:
    model = Birthday
    



class BirthdayCreateView(LoginRequiredMixin, BirthdayMixin, CreateView):
    form_class = BirthdayForm
    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form) 


class BirthdayUpdateView(LoginRequiredMixin, BirthdayMixin, UpdateView):
    form_class = BirthdayForm
    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Birthday, pk=kwargs['pk'], author=request.user)
        # Если объект был найден, то вызываем родительский метод, 
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)


class BirthdayDeleteView(LoginRequiredMixin, BirthdayMixin, DeleteView):
    success_url = reverse_lazy('birthday:list')
    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Birthday, pk=kwargs['pk'], author=request.user)
        # Если объект был найден, то вызываем родительский метод, 
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_countdown'] = calculate_birthday_countdown(
            self.object.birthday
        )
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context 
    
@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')

@login_required
def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    birthday = get_object_or_404(Birthday, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    form = CongratulationForm(request.POST)
    if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        congratulation = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        congratulation.author = request.user
        # В поле birthday передаём объект дня рождения.
        congratulation.birthday = birthday
        # Сохраняем объект в БД.
        congratulation.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('birthday:detail', pk=pk) 


class CongratulationCreateView(LoginRequiredMixin, CreateView):
    birthday = None
    model = Congratulation
    form_class = CongratulationForm

    # Переопределяем dispatch()
    def dispatch(self, request, *args, **kwargs):
        self.birthday = get_object_or_404(Birthday, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.birthday = self.birthday
        return super().form_valid(form)

    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('birthday:detail', kwargs={'pk': self.birthday.pk}) 