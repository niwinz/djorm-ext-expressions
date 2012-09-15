=====================
djorm-ext-expressions
=====================

Django by default, provides a wide range of field types and generic lookups for queries. This in many cases is more than enough. But there are cases where you need to use types defined for yourself and search operators that are not defined in django lookups and another important case is to make searches requiring the execution of some function in WHERE clause.

In django, for these last two cases, it requires writing SQL statements. ``djorm-ext-expressions``  introduces the method ``manager.where()`` and some class'es (SqlExpression, SqlFunction, AND, OR, ...) to facilite sql construction for advanced cases.

Simple usage
------------

Imagine some django model with postgresql integer array field. You need to find objects in the field containing a set of group numbers.

**NOTE**: array field is part of django orm extensions package and is located on ``djorm-ext-pgarray`` submodule.

**Example model definition**

.. code-block:: python

    from django.db import models
    from djorm_expressions.models import ExpressionManager
    from .somefiels import ArrayField

    class Register(models.Model):
        name = models.CharField(max_length=200)
        points = ArrayField(dbtype="int")

        objects = ExpressionManager()


With this model definition, we can do this searches:

.. code-block:: python

    from djorm_expressions.base import SqlExpression, AND, OR

    # search all register items that points field contains [2,3]

    qs = Register.manager.where(
        SqlExpression("points", "@>", [2,3])
    )

    # search all register items that points fields contains [2,3] or [5,6]

    expression = OR(
        SqlExpression("points", "@>", [2,3]),
        SqlExpression("points", "@>", [5,6]),
    )

    qs = Register.objects.where(expression)


Also, we can use functions to construct a expression:

.. code-block:: python

    from djorm_expressions.base import SqlFunction

    class BitLength(SqlFunction):
        sql_function = "bit_length"

    # search all registers items that bit_length(name) > 20.
    qs = Register.objects.where(
        SqlExpression(BitLength("name"), ">", 20)
    )


I finally can redefine the behavior "SqlExpression" and make it more "object oriented":

.. code-block:: python

    class ArrayExpression(object):
        def __init__(self, field):
            self.field = field

        def contains(self, value):
            return SqlExpression(self.field, "@>", value)

        def overlap(self, value):
            return SqlExpression(self.field, "&&", value)

    # search all register items that points field contains [2,3]
    qs = Register.objects.where(
        ArrayExpression("points").contains([2,3])
    )
