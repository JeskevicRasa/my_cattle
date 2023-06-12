from django.db import models


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Cattle(models.Model):
    GENDER = [
        ('Female', 'Female'),
        ('Male', 'Male'),
    ]

    ACQUISITION_METHOD = [
        ('Birth', 'Birth'),
        ('Purchase', 'Purchase'),
        ('Gift', 'Gift'),
    ]

    LOSS_METHOD = [
        ('Death', 'Death'),
        ('Sold', 'Sold'),
        ('Consumed', 'Consumed'),
        ('Gifted', 'Gifted'),
    ]

    type = models.CharField(max_length=80, blank=False)
    number = models.CharField(max_length=80, blank=False, unique=True)
    name = models.CharField(max_length=80, blank=False)
    gender = models.CharField(choices=GENDER, max_length=80, blank=False)
    breed = models.CharField(max_length=80, blank=False)
    birth_date = models.DateField()
    acquisition_method = models.CharField(choices=ACQUISITION_METHOD, max_length=80, blank=True, null=True)
    entry_date = models.DateField()
    loss_method = models.CharField(choices=LOSS_METHOD, max_length=80, blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    comments = models.TextField(max_length=2000)

    class Meta:
        verbose_name = "Cattle Info"
        verbose_name_plural = "Cattle Info"
        ordering = ['name']

    def __str__(self):
        return f'{self.name},  {self.gender}, {self.birth_date}'


