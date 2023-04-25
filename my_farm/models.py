from django.db import models

GENDER = [
    ('Female', 'Female'),
    ('Male', 'Male'),
]


class Cattle(models.Model):
    type = models.CharField(max_length=80, blank=False)
    number = models.CharField(max_length=80, blank=False, unique=True)
    name = models.CharField(max_length=80, blank=False)
    gender = models.CharField(choices=GENDER, max_length=80,blank=False)
    breed = models.CharField(max_length=80, blank=False)
    birth_date = models.DateField()
    entry_date = models.DateField()
    end_date = models.DateField()
    comments = models.TextField(max_length=2000)

    class Meta:
        verbose_name = "Cattle Info"
        verbose_name_plural = "Cattle Info"
        ordering = ['name']

    def __str__(self):
        return f' {self.name},  {self.gender}, {self.birth_date}'


