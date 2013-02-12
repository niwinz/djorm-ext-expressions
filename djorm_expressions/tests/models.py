# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models

from ..models import ExpressionManager

class Person(models.Model):
    name = models.CharField(max_length=200)
    objects = ExpressionManager()


class Profile(models.Model):
    person = models.ForeignKey("Person", related_name="profiles")
    objects = ExpressionManager()


class Node(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey("self", related_name="childs",
                                        null=True, default=None)

    objects = ExpressionManager()
