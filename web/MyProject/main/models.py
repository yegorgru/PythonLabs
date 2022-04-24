from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=20)


class Employee(models.Model):
    name = models.CharField(max_length=20)
    rank = models.IntegerField()
    experience = models.IntegerField()
    unitId = models.IntegerField()