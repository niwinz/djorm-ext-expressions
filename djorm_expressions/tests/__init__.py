# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.db.models import Q

from djorm_expressions.base import  RawExpression, SqlExpression, SqlFunction, AND, OR
from .models import Person, Profile, Node


class BitLength(SqlFunction):
    sql_function = "bit_length"


class SqlExpressionsTests(TestCase):
    def setUp(self):
        Person.objects.all().delete()

    def test_raw_statements_0(self):
        expresion_instance = OR(
            AND(
                RawExpression("name = %s", "Foo"),
                RawExpression("age = %s", 14),
            ),
            AND(
                RawExpression("name = %s", "Bar"),
                RawExpression("age = %s", 14),
            )
        )
        sql, params = expresion_instance.as_sql(None, None)
        self.assertEqual(sql.to_str(), "(name = %s AND age = %s) OR (name = %s AND age = %s)")
        self.assertEqual(params, ['Foo', 14, 'Bar', 14])


    def test_string_sample_statement(self):
        obj = Person.objects.create(name="jose")

        queryset = Person.objects.where(
            SqlExpression(BitLength("name"), "=", 32)
        )
        self.assertEqual(queryset.count(), 1)

    def test_join_lookup_with_expression_01(self):
        person = Person.objects.create(name="jose")
        profile = Profile.objects.create(person=person)

        queryset = Profile.objects.where(
            SqlExpression(BitLength("person__name"), "=", 32)
        )
        self.assertEqual(queryset.count(), 1)

    def test_join_lookup_with_expression_02(self):
        node1 = Node.objects.create(name="master1")
        node2 = Node.objects.create(name="master2")
        node3 = Node.objects.create(name="child1", parent=node1)
        node4 = Node.objects.create(name="child2", parent=node2)

        queryset = Node.objects.where(
            SqlExpression("parent__name", "=", "master1")
        )

        self.assertEqual(queryset.count(), 1)

    def test_join_lookup_with_expression_03(self):
        node1 = Node.objects.create(name="master1")
        node2 = Node.objects.create(name="master2")
        node3 = Node.objects.create(name="child1", parent=node1)
        node4 = Node.objects.create(name="child2", parent=node2)

        expr = OR(SqlExpression("parent__name", "=", "master1"),
                    SqlExpression("name", "=", "child1"))

        queryset = Node.objects.where(expr)
        self.assertEqual(queryset.count(), 1)
