from django.db import models


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class CattleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class Cattle(models.Model):

    BREED = [
        ('Angus', 'Angus'),
        ('Crossbreed', 'Crossbreed'),
    ]

    GENDER = [
        ('Heifer', 'Heifer'),
        ('Bull', 'Bull'),
        ('Cow', 'Cow'),
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

    type = models.CharField(default='Cattle', max_length=80, blank=False)
    number = models.CharField(max_length=80, blank=False, unique=True)
    name = models.CharField(max_length=80, blank=True, null=True)
    gender = models.CharField(choices=GENDER, max_length=80, blank=False)
    breed = models.CharField(choices=BREED, max_length=80, blank=False)
    birth_date = models.DateField(blank=True, null=True)
    acquisition_method = models.CharField(choices=ACQUISITION_METHOD, max_length=80, blank=True, null=True)
    entry_date = models.DateField(blank=True, null=True)
    herd = models.ForeignKey('Herd', on_delete=models.SET_NULL, blank=True, null=True)
    loss_method = models.CharField(choices=LOSS_METHOD, max_length=80, blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    comments = models.TextField(max_length=2000)
    deleted = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='cattle_pictures', blank=True, null=True)

    def delete(self):
        self.deleted = True
        self.save()

    class Meta:
        verbose_name = "Cattle Info"
        verbose_name_plural = "Cattle Info"
        ordering = ['name']

    def __str__(self):
        return f'{self.name},  {self.gender}, {self.birth_date}'


class Field(models.Model):

    SIZE_CHOICES = [
            ('ha', 'Hectares'),
            ('ac', 'Acres'),
        ]

    name = models.CharField(max_length=80, blank=False)
    location = models.CharField(max_length=100, blank=False)
    coordinates = models.CharField(max_length=100, blank=False)
    field_size = models.FloatField(blank=True, null=True)
    size_unit = models.CharField(choices=SIZE_CHOICES, max_length=2, blank=True)
    field_type = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(max_length=1200, blank=True)
    picture = models.ImageField(upload_to='field_pictures', blank=True, null=True)

    def __str__(self):
        return self.name


class Herd(models.Model):
    name = models.CharField(max_length=80, blank=False)
    location = models.CharField(max_length=100, blank=False)
    field = models.ForeignKey('Field', on_delete=models.SET_NULL, blank=True, null=True, related_name='field_herds')
    description = models.TextField(max_length=2000, blank=True)
    start_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    herd_leader = models.ForeignKey('Cattle', on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name='herd_leader')
    picture = models.ImageField(upload_to='herd_pictures', blank=True, null=True)

    def __str__(self):
        return self.name



class CattleMovementReport(models.Model):
    title = models.CharField(max_length=100)
    generated_date = models.DateTimeField(auto_now_add=True)
    report_data = models.JSONField()