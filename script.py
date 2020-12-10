import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = 'vacancies.settings'
django.setup()

from app_vacancy.models import Vacancy
from app_vacancy.models import Company
from app_vacancy.models import Specialty

from data import jobs
from data import companies
from data import specialties

if __name__ == '__main__':

    num_of_jobs = len(jobs)
    num_of_spec = len(specialties)
    num_of_companies = len(companies)
    spec_set = set()
    companies_set_for_vac = set()
    companies_set_for_others = set()
    passing_comp = 0
    for job in range(num_of_jobs):
        for spec in range(num_of_spec):
            if jobs[job]['specialty'] == specialties[spec]['code']:
                for comp in range(num_of_companies):
                    if jobs[job]['company'] == companies[comp]['id']:
                        company_for_vac = Company(
                            name=companies[comp]['title'],
                            location=companies[comp]['location'],
                            description=companies[comp]['description'],
                            employee_count=int(companies[comp]['employee_count']),
                        )
                        companies_set_for_vac.add(companies[comp]['id'])
                        company_for_vac.save()

                        if specialties[spec]['code'] not in spec_set:
                            specialty_for_vac = Specialty(
                                code=specialties[spec]['code'],
                                title=specialties[spec]['title'],
                            )
                            spec_set.add(specialties[spec]['code'])
                            specialty_for_vac.save()

                        vacancy = Vacancy(
                            title=jobs[job]['title'],
                            specialty=specialty_for_vac,
                            company=company_for_vac,
                            skills=jobs[job]['skills'],
                            description=jobs[job]['description'],
                            salary_min=int(jobs[job]['salary_from']),
                            salary_max=int(jobs[job]['salary_to']),
                            published_at=jobs[job]['posted'],
                        )
                        vacancy.save()

                        if passing_comp > 0:
                            for comp_without_vac in range(1, num_of_companies):
                                if companies[comp_without_vac]['id'] in companies_set_for_others:
                                    pass
                                elif companies[comp_without_vac]['id'] not in companies_set_for_vac:
                                    company_without_vac = Company(
                                        name=companies[comp_without_vac]['title'],
                                        location=companies[comp_without_vac]['location'],
                                        description=companies[comp_without_vac]['description'],
                                        employee_count=int(companies[comp_without_vac]['employee_count']),
                                    )
                                    companies_set_for_others.add(companies[comp_without_vac]['id'])
                                    company_without_vac.save()
                                    break
                        passing_comp += 1

            elif specialties[spec]['code'] not in spec_set:
                specialty_without_vac = Specialty(
                    code=specialties[spec]['code'],
                    title=specialties[spec]['title'],
                )
                spec_set.add(specialties[spec]['code'])
                specialty_without_vac.save()
