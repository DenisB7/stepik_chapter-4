from random import sample

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponseNotFound, HttpResponseServerError, Http404
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from app_vacancy.forms import RegisterUserForm, ApplicationForm, MyCompanyForm, MyCompanyVacanciesCreateEditForm, \
    MyResumeForm
from app_vacancy.models import Company, Specialty, Vacancy, Application


# Public starts here

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
            for skill in skills_split:
                set_of_skills.add(skill)
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
        vacs_of_spec = Specialty.objects.filter(code=specialty)
        if not vacs_of_spec:
            raise Http404
        vacancies_of_spec = {'vacs_of_spec': vacs_of_spec}
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
        except:
            raise Http404


class SendRequestView(View):

    def get(self, request, id):
        try:
            vacancy_id = {'vacancy_id': id}
            return render(request, 'sent.html', context=vacancy_id)
        except:
            raise Http404


class OneVacancyView(View):

    def get(self, request, id):
        try:
            vacancy = Vacancy.objects.get(id=id)
            form = ApplicationForm()
            vac_and_form = {'vac': vacancy, 'form': form}
            return render(request, 'vacancy.html', context=vac_and_form)
        except:
            raise Http404

    def post(self, request, id):
        vac = Vacancy.objects.get(id=id)
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy_id = id
            application.user_id = vac.company.owner_id
            application.save()
            return redirect(f"/vacancies/{id}/sent")

        vac_and_form = {'vac': vac, 'form': form}
        return render(request, 'vacancy.html', context=vac_and_form)


# Public ends here

# Resume starts here

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
        except:
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
        except:
            return redirect('/myresume/start')

    def post(self, request):
        owner = request.user
        form = MyResumeForm(request.POST)
        if form.is_valid():
            my_resume = form.save(commit=False)
            my_resume.id = owner.resumes.id
            my_resume.user = owner
            my_resume.save()
            messages.success(request, 'Ваше резюме обновлено!')
            return redirect(request.path)

        my_resume = owner.resumes
        form = MyResumeForm(instance=my_resume)
        messages.error(request, 'ОШИБКА! Ваше резюме не обновлено!')
        return render(request, 'resume-edit.html', {'form': form})


# Resume ends here

# Register/auth starts here

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


# Register/auth ends here


# MyCompany create/edit starts here

class MyCompany(View):

    @method_decorator(login_required)
    def get(self, request):
        try:
            my_company = request.user.company
            form = MyCompanyForm(instance=my_company)
            return render(request, 'company-edit.html', {'form': form})
        except:
            return redirect('/mycompany/start')

    def post(self, request):
        owner = request.user
        form = MyCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            my_company = form.save(commit=False)
            my_company.id = owner.company.id
            my_company.owner = owner
            my_company.save()
            messages.success(request, 'Информация о компании обновлена!')
            return redirect(request.path)

        my_company = owner.company
        form = MyCompanyForm(instance=my_company)
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
        except:
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


# MyCompany create/edit ends here


# MyCompany Vacancies create/edit starts here

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
        context = {'vacancies_list': vacancies_list}
        return render(request, 'vacancy-list.html', context=context)


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
            applications = Application.objects.filter(vacancy_id=id).values('written_username', 'written_phone',
                                                                            'written_cover_letter')
            context = {'form': form, 'vacancy_title': vacancy.title, 'applications': applications}
            return render(request, 'vacancy-edit.html', context=context)
        except:
            raise Http404

    def post(self, request, id):
        company_id = request.user.company.id
        form = MyCompanyVacanciesCreateEditForm(request.POST)
        if form.is_valid():
            my_comp_vac = form.save(commit=False)
            my_comp_vac.id = id
            my_comp_vac.company_id = company_id
            my_comp_vac.save()
            messages.success(request, 'Поздравляем! Вы обновили информацию о вакансии')
            return redirect(request.path)

        vacancy = Vacancy.objects.get(id=id)
        form = MyCompanyVacanciesCreateEditForm(instance=vacancy)
        applications = Application.objects.filter(vacancy_id=id).values('written_username', 'written_phone',
                                                                        'written_cover_letter')
        messages.error(request, 'ОШИБКА! Вакансия не обновлена!')
        context = {'form': form, 'vacancy_title': vacancy.title, 'applications': applications}
        return render(request, 'vacancy-edit.html', context=context)


# MyCompany Vacancies create/edit ends here

def custom_handler404(request, exception):
    return HttpResponseNotFound('404 ошибка - ошибка на стороне '
                                'сервера (страница не найдена)')


def custom_handler500(request):
    return HttpResponseServerError('внутренняя ошибка сервера')
