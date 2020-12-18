from random import sample

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseNotFound, HttpResponseServerError, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from app_vacancy.forms import ApplicationForm
from app_vacancy.forms import MyCompanyForm
from app_vacancy.forms import MyCompanyVacanciesCreateEditForm
from app_vacancy.forms import MyResumeForm
from app_vacancy.forms import RegisterUserForm

from app_vacancy.models import Application, Company, Specialty, Vacancy


class MainView(View):

    def get(self, request):
        query = request.GET.get('search')
        if query:
            specialties = Specialty.objects.filter(title__icontains=query)
            companies = Company.objects.filter(name__icontains=query)
        else:
            specialties = Specialty.objects.all()
            companies = Company.objects.all()
        skills = Vacancy.objects.values('skills')
        set_of_skills = set()
        for skills_list in skills:
            skills_split = skills_list['skills'].split(', ')
            set_of_skills.update(skills_split)
        skills_random = sample(set_of_skills, 5)
        main = {
            'specialties': specialties,
            'companies': companies,
            'skills_random': skills_random
        }
        return render(request, 'index.html', context=main)


class SearchView(View):

    def get(self, request):
        query = request.GET.get('search')
        if query:
            vacancies = Vacancy.objects.filter(Q(title__icontains=query) | Q(skills__icontains=query))
            if not vacancies:
                vacancies = Vacancy.objects.filter(specialty__title__icontains=query)
        else:
            vacancies = Vacancy.objects.all()
        return render(request, 'search.html', {'vacancies': vacancies})


class AllVacanciesView(View):

    def get(self, request):
        vacancies = Vacancy.objects.all()
        all_vacancies = {'vacancies': vacancies}
        return render(request, 'vacancies.html', context=all_vacancies)


class VacanciesSpecView(View):

    def get(self, request, specialty):
        spec = get_object_or_404(Specialty, code=specialty)
        vacs_of_spec = spec.vacancies.all()
        vacs_of_spec_amount = vacs_of_spec.count()
        vacancies_of_spec = {
            'spec': spec,
            'vacs_of_spec': vacs_of_spec,
            'vacs_of_spec_amount': vacs_of_spec_amount
        }
        return render(request, 'vacsspec.html', context=vacancies_of_spec)


class CompaniesView(View):

    def get(self, request, id):
        try:
            company = Company.objects.get(id=id)
            vacs_of_company = company.vacancies.all()
            companies = {
                'company': company,
                'vacs_of_company': vacs_of_company
            }
            return render(request, 'company.html', context=companies)
        except ObjectDoesNotExist:
            raise Http404


class SendRequestView(View):

    def get(self, request, id):
        try:
            vacancy_id = {'vacancy_id': id}
            return render(request, 'sent.html', context=vacancy_id)
        except ObjectDoesNotExist:
            raise Http404


class OneVacancyView(View):

    def get(self, request, id):
        try:
            vacancy = Vacancy.objects.get(id=id)
            company = vacancy.company
            form = ApplicationForm()
            vac_and_form = {
                'vacancy': vacancy,
                'company': company,
                'form': form,
            }
            return render(request, 'vacancy.html', context=vac_and_form)
        except ObjectDoesNotExist:
            raise Http404

    def post(self, request, id):
        vacancy = Vacancy.objects.get(id=id)
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy_id = id
            application.user_id = vacancy.company.owner_id
            application.save()
            return redirect(f"/vacancies/{id}/sent")

        company = vacancy.company
        vac_and_form = {
            'vacancy': vacancy,
            'company': company,
            'form': form
        }
        return render(request, 'vacancy.html', context=vac_and_form)


class ResumeStartView(View):

    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'resume-start.html')


class ResumeCreateView(View):

    @method_decorator(login_required)
    def get(self, request):
        try:
            have_got_resume = request.user.resumes
            return redirect('/myresume')
        except ObjectDoesNotExist:
            form = MyResumeForm()
            return render(request, 'resume-create.html', {'form': form})

    def post(self, request):
        owner = request.user
        form = MyResumeForm(request.POST)
        if form.is_valid():
            new_resume = form.save(commit=False)
            new_resume.user = owner
            new_resume.save()
            messages.success(request, 'Резюме создано')
            return redirect('/myresume')

        messages.error(request, 'ОШИБКА! Резюме не создано')
        return render(request, 'resume-create.html', {'form': form})


class ResumeEditView(View):

    @method_decorator(login_required)
    def get(self, request):
        try:
            my_resume = request.user.resumes
            form = MyResumeForm(instance=my_resume)
            return render(request, 'resume-edit.html', {'form': form})
        except ObjectDoesNotExist:
            return redirect('/myresume/start')

    def post(self, request):
        owner = request.user
        form = MyResumeForm(request.POST, instance=owner.resumes)
        if form.is_valid():
            my_resume = form.save(commit=False)
            my_resume.user = owner
            my_resume.save()
            messages.success(request, 'Ваше резюме обновлено!')
            return redirect(request.path)

        messages.error(request, 'ОШИБКА! Ваше резюме не обновлено!')
        return render(request, 'resume-edit.html', {'form': form})


class MyLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'


class RegisterUserView(View):

    def get(self, request):
        form = RegisterUserForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')

        return render(request, 'register.html', {'form': form})


class MyCompany(View):

    @method_decorator(login_required)
    def get(self, request):
        try:
            my_company = request.user.company
            form = MyCompanyForm(instance=my_company)
            return render(request, 'company-edit.html', {'form': form})
        except ObjectDoesNotExist:
            return redirect('/mycompany/start')

    def post(self, request):
        owner = request.user
        form = MyCompanyForm(request.POST, request.FILES, instance=owner.company)
        if form.is_valid():
            my_company = form.save(commit=False)
            my_company.owner = owner
            my_company.save()
            messages.success(request, 'Информация о компании обновлена!')
            return redirect(request.path)

        messages.error(request, 'ОШИБКА! Информация о компании не обновлена!')
        return render(request, 'company-edit.html', {'form': form})


class MyCompanyStart(View):

    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'company-start.html')


class MyCompanyStartCreate(View):

    @method_decorator(login_required)
    def get(self, request):
        try:
            have_got_company = request.user.company
            return redirect('/mycompany')
        except ObjectDoesNotExist:
            form = MyCompanyForm()
            return render(request, 'company-create.html', {'form': form})

    def post(self, request):
        owner = request.user
        form = MyCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            new_company = form.save(commit=False)
            new_company.owner = owner
            new_company.save()
            messages.success(request, 'Поздравляем! Вы создали компанию')
            return redirect('/mycompany')

        messages.error(request, 'ОШИБКА! Компания не создана!')
        return render(request, 'company-create.html', {'form': form})


class MyCompanyVacancies(View):

    @method_decorator(login_required)
    def get(self, request):
        vacancies = Vacancy.objects.filter(company__owner=request.user)
        if not vacancies:
            return redirect('/mycompany/vacancies/start')
        vacancies_list = []
        for vacancy in vacancies:
            vacancy_dict = {
                'id': vacancy.id,
                'title': vacancy.title,
                'salary_min': vacancy.salary_min,
                'salary_max': vacancy.salary_max,
                'applications': Application.objects.filter(vacancy_id=vacancy.id).count()
            }
            vacancies_list.append(vacancy_dict)
        mycomp_vacs = {'vacancies_list': vacancies_list}
        return render(request, 'vacancy-list.html', context=mycomp_vacs)


class MyCompanyVacanciesStart(View):

    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'vacancy-start.html')


class MyCompanyVacancyCreate(View):

    @method_decorator(login_required)
    def get(self, request):
        have_got_vacancy = Vacancy.objects.filter(company__owner_id=request.user.id)
        if have_got_vacancy:
            return redirect('/mycompany/vacancies')
        else:
            form = MyCompanyVacanciesCreateEditForm()
            return render(request, 'vacancy-create.html', {'form': form})

    def post(self, request):
        owner = request.user
        form = MyCompanyVacanciesCreateEditForm(request.POST)
        if form.is_valid():
            vacancy_create = form.save(commit=False)
            vacancy_create.company_id = owner.company.id
            vacancy_create.save()
            messages.success(request, 'Поздравляем! Вы создали вакансию')
            return redirect('/mycompany/vacancies')

        messages.error(request, 'ОШИБКА! Вакансия не создана!')
        return render(request, 'vacancy-create.html', {'form': form})


class MyCompanyOneVacancy(View):

    @method_decorator(login_required)
    def get(self, request, id):
        try:
            alien_company = request.user.company.id
            vacancy = Vacancy.objects.get(id=id)
            if alien_company != vacancy.company_id:
                return redirect('/mycompany/vacancies')
            form = MyCompanyVacanciesCreateEditForm(instance=vacancy)
            applications = Application.objects.filter(vacancy_id=id) \
                .values(
                'written_username',
                'written_phone',
                'written_cover_letter'
            )
            context = {
                'form': form,
                'vacancy_title': vacancy.title,
                'applications': applications
            }
            return render(request, 'vacancy-edit.html', context=context)
        except ObjectDoesNotExist:
            raise Http404

    def post(self, request, id):
        company_id = request.user.company.id
        vacancy = Vacancy.objects.get(id=id)
        form = MyCompanyVacanciesCreateEditForm(request.POST, instance=vacancy)
        if form.is_valid():
            my_comp_vac = form.save(commit=False)
            my_comp_vac.company_id = company_id
            my_comp_vac.save()
            messages.success(request, 'Поздравляем! Вы обновили информацию о вакансии')
            return redirect(request.path)

        applications = Application.objects.filter(vacancy_id=id) \
            .values(
            'written_username',
            'written_phone',
            'written_cover_letter'
        )
        one_vacancy = {
            'form': form,
            'vacancy_title': vacancy.title,
            'applications': applications
        }
        messages.error(request, 'ОШИБКА! Информация о вакансии не обновлена!')
        return render(request, 'vacancy-edit.html', context=one_vacancy)


def custom_handler404(request, exception):
    return HttpResponseNotFound('404 ошибка - ошибка на стороне '
                                'сервера (страница не найдена)')


def custom_handler500(request):
    return HttpResponseServerError('внутренняя ошибка сервера')
