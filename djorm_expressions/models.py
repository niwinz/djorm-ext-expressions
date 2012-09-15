# -*- coding: utf-8 -*-

from django.utils.datastructures import SortedDict
from django.db.models.sql.where import ExtraWhere
from django.db.models.query import QuerySet
from django.db import models

from .base import AND


class ExpressionQuerySetMixin(object):
    def annotate_functions(self, **kwargs):
        extra_select, params = SortedDict(), []
        clone = self._clone()

        for alias, node in kwargs.iteritems():
            _sql, _params = node.as_sql(self.quote_name, self)

            extra_select[alias] = _sql
            params.extend(_params)

        clone.query.add_extra(extra_select, params, None, None, None, None)
        return clone

    def where(self, *args):
        clone = self._clone()
        statement = AND(*args)

        _sql, _params = statement.as_sql(self.quote_name, clone)
        if hasattr(_sql, 'to_str'):
            _sql = _sql.to_str()

        clone.query.where.add(ExtraWhere([_sql], _params), "AND")
        return clone

    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name # Quoting once is enough.
        return '"%s"' % name



class ExpressionManagerMixin(object):
    def annotate_functions(self, **kwargs):
        return self.get_query_set().annotate_functions(**kwargs)

    def where(self, *args):
        return self.get_query_set().where(*args)


class ExpressionQuerySet(ExpressionQuerySetMixin, QuerySet):
    """
    Predefined expression queryset. Usefull if you only use expresions.
    """
    pass


class ExpressionManager(ExpressionManagerMixin, models.Manager):
    """
    Prededined expression manager what uses `ExpressionQuerySet`.
    """

    use_for_related_fields = True

    def get_query_set(self):
        return ExpressionQuerySet(model=self.model, using=self._db)
