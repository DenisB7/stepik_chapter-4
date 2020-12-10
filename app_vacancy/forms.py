from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from app_vacancy.models import Application, Company, Vacancy, Resume


class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=20, label='Имя')
    last_name = forms.CharField(max_length=20, label='Фамилия')
    email = forms.EmailField(label='Адрес электронной почты')

    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email')


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        exclude = ('vacancy', 'user')
        labels = {
            'written_username': 'Ваше ФИО (фамилия, имя, отчество)',
            'written_phone': 'Ваш номер телефона',
            'written_cover_letter': 'Сопроводительное письмо',
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(
                Row(
                    Column('written_username', ),
                ),
                Row(
                    Column('written_phone', ),
                ),
                Row(
                    Column('written_cover_letter', ),
                ),
            )


class MyCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        exclude = ('owner',)
        labels = {
            'name': 'Название компании',
            'logo': 'Логотип',
            'location': 'География',
            'description': 'Информация о компании',
            'employee_count': 'Количество человек в компании',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', ),
                Column('logo', ),
            ),
            Row(
                Column('employee_count', ),
                Column('location', ),
            ),
            Row(
                Column('description', ),
            ),
            Row(
                Column(Submit('submit', 'Сохранить')),
            ),
        )


class MyCompanyVacanciesCreateEditForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        exclude = ('company', 'published_at')
        labels = {
            'title': 'Название вакансии',
            'specialty': 'Специализация',
            'skills': 'Требуемые навыки',
            'description': 'Описание вакансии',
            'salary_min': 'Зарплата от',
            'salary_max': 'Зарплата до',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', ),
                Column('specialty', ),
            ),
            Row(
                Column('salary_min', ),
                Column('salary_max', ),
            ),
            Row(
                Column('skills', ),
            ),
            Row(
                Column('description', ),
            ),
            Row(
                Column(Submit('submit', 'Сохранить')),
            ),
        )


STATUSES = (
    ('', '---------'),
    ('Не ищу работу', 'Не ищу работу'),
    ('Рассматриваю предложения', 'Рассматриваю предложения'),
    ('Ищу работу', 'Ищу работу')
)

GRADES = (
    ('', '---------'),
    ('Стажер', 'Стажер'),
    ('Джуниор', 'Джуниор'),
    ('Миддл', 'Миддл'),
    ('Синьор', 'Синьор'),
    ('Лид', 'Лид')
)


class MyResumeForm(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUSES)
    grade = forms.ChoiceField(choices=GRADES)

    class Meta:
        model = Resume
        exclude = ('user',)
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'status': 'Готовность к работе',
            'salary': 'Вознаграждение',
            'specialty': 'Специализация',
            'grade': 'Квалификация',
            'education': 'Образование',
            'experience': 'Опыт работы',
            'portfolio': 'Портфолио'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', ),
                Column('surname', ),
            ),
            Row(
                Column('status', ),
                Column('salary', ),
            ),
            Row(
                Column('specialty', ),
                Column('grade', )
            ),
            Row(
                Column('education', ),
            ),
            Row(
                Column('experience', ),
            ),
            Row(
                Column('portfolio', ),
            ),
            Row(
                Column(Submit('submit', 'Сохранить')),
            ),
        )
