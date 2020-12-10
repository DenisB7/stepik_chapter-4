"""vacancies URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from app_vacancy.views import custom_handler404, custom_handler500, MainView, SearchView, ResumeEditView, \
    ResumeStartView, ResumeCreateView, AllVacanciesView, VacanciesSpecView, CompaniesView, OneVacancyView, \
    SendRequestView, MyCompany, MyCompanyStart, MyCompanyStartCreate, MyCompanyVacancies, MyCompanyVacanciesStart, \
    MyCompanyVacancyCreate, MyCompanyOneVacancy, MyLoginView, RegisterUserView

handler404 = custom_handler404
handler500 = custom_handler500

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('search', SearchView.as_view(), name='search'),
    path('myresume', ResumeEditView.as_view(), name='resume'),
    path('myresume/start', ResumeStartView.as_view(), name='resume_start'),
    path('myresume/create', ResumeCreateView.as_view(), name='resume_create'),
    path('vacancies', AllVacanciesView.as_view(), name='all_vacancies'),
    path('vacancies/cat/<str:specialty>/', VacanciesSpecView.as_view(), name='vacancies_by_specialty'),
    path('companies/<int:id>/', CompaniesView.as_view(), name='company'),
    path('vacancies/<int:id>/', OneVacancyView.as_view(), name='vacancy'),
    path('vacancies/<int:id>/sent', SendRequestView.as_view(), name='send_request'),
    path('mycompany', MyCompany.as_view(), name='my_company'),
    path('mycompany/start', MyCompanyStart.as_view(), name='company_start'),
    path('mycompany/create', MyCompanyStartCreate.as_view(), name='company_create'),
    path('mycompany/vacancies', MyCompanyVacancies.as_view(), name='my_vacancies'),
    path('mycompany/vacancies/start', MyCompanyVacanciesStart.as_view(), name='my_vacancies_start'),
    path('mycompany/vacancies/create', MyCompanyVacancyCreate.as_view(), name='my_vacancies_create'),
    path('mycompany/vacancies/<int:id>/', MyCompanyOneVacancy.as_view(), name='my_one_vacancy'),
    path('login', MyLoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('register', RegisterUserView.as_view()),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
