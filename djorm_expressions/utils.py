# -*- coding: utf-8 -*-

from django.db.models.fields import FieldDoesNotExist

def _setup_joins_for_fields(parts, node, queryset):
    """
    Method ported from django 1.4 for correct setup joins.
    """

    parts_num = len(parts)

    if parts_num == 0:
        return

    if parts_num == 1:
        node.field = (queryset.model._meta.db_table, parts[0])

    field, source, opts, join_list, last, _ = queryset.query.setup_joins(
        parts, queryset.model._meta, queryset.query.get_initial_alias(), False)

    # Process the join chain to see if it can be trimmed
    col, _, join_list = queryset.query.trim_joins(source, join_list, last, False)

    # If the aggregate references a model or field that requires a join,
    # those joins must be LEFT OUTER - empty join rows must be returned
    # in order for zeros to be returned for those aggregates.
    for column_alias in join_list:
        queryset.query.promote_alias(column_alias, unconditional=True)

    # this works for one level of depth
    #lookup_model = self.query.model._meta.get_field(parts[-2]).rel.to
    #lookup_field = lookup_model._meta.get_field(parts[-1])

    if parts_num >= 2:
        lookup_model = queryset.model
        for counter, field_name in enumerate(parts):
            try:
                lookup_field = lookup_model._meta.get_field(field_name)
            except FieldDoesNotExist:
                parts.pop()
                break

            try:
                lookup_model = lookup_field.rel.to
            except AttributeError:
                parts.pop()
                break

        node.field = (lookup_model._meta.db_table, lookup_field.attname)
