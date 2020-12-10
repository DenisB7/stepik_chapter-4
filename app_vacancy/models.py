from django.db import models
from django.contrib.auth import get_user_model


class Company(models.Model):
    name = models.CharField(max_length=64)
    location = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='company_images')
    description = models.TextField()
    employee_count = models.PositiveIntegerField()
    owner = models.OneToOneField(get_user_model(), null=True, on_delete=models.CASCADE, related_name='company')


class Specialty(models.Model):
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=12)
    picture = models.ImageField(upload_to='speciality_images')

    def __str__(self):
        return self.title


class Vacancy(models.Model):
    title = models.CharField(max_length=29)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='vacancies')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies')
    skills = models.CharField(max_length=75)
    description = models.TextField()
    salary_min = models.PositiveIntegerField()
    salary_max = models.PositiveIntegerField()
    published_at = models.CharField(max_length=10)


class Application(models.Model):
    written_username = models.CharField(max_length=50)
    written_phone = models.CharField(max_length=50)
    written_cover_letter = models.TextField()
    vacancy = models.ForeignKey(Vacancy, null=True, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.CASCADE, related_name='applications')


class Resume(models.Model):
    user = models.OneToOneField(get_user_model(), null=True, on_delete=models.CASCADE, related_name='resumes')
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    salary = models.PositiveIntegerField()
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='resumes')
    grade = models.CharField(max_length=50)
    education = models.TextField()
    experience = models.TextField()
    portfolio = models.URLField()
