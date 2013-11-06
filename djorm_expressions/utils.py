# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django
from django.db.models.fields import FieldDoesNotExist


def _setup_joins_for_fields(parts, node, queryset):
    version = django.VERSION[:2]
    version_lt_1_5, version_gt_1_5 = version < (1, 5), version >= (1, 6)

    parts_num = len(parts)
    if parts_num == 0:
        return

    if parts_num == 1:
        node.field = (queryset.model._meta.db_table, parts[0])

    setup_joins_args = (parts, queryset.model._meta,
                        queryset.query.get_initial_alias())
    if version_gt_1_5:
        # Django 1.6+ compatibility.
        field, source, opts, join_list, last = queryset.query.setup_joins(
            *setup_joins_args)
    else:
        field, source, opts, join_list, last, _ = queryset.query.setup_joins(
            *setup_joins_args, dupe_multis=False)

    # Process the join chain to see if it can be trimmed
    if version_gt_1_5:
        # Django 1.6+ compatibility.
        trim_joins_args = source, join_list, last
    else:
        trim_joins_args = source, join_list, last, False

    col, alias, join_list = queryset.query.trim_joins(*trim_joins_args)

    if version_lt_1_5:
        for column_alias in join_list:
            queryset.query.promote_alias(column_alias, unconditional=True)
    else:
        # Django 1.5+ compatibility
        queryset.query.promote_joins(join_list, unconditional=True)

    # this works for one level of depth
    #lookup_model = self.query.model._meta.get_field(parts[-2]).rel.to
    #lookup_field = lookup_model._meta.get_field(parts[-1])

    if parts_num >= 2:
        lookup_model = queryset.model
        for counter, field_name in enumerate(parts):
            try:
                lookup_field = lookup_model._meta.get_field_by_name(field_name)[0]
                if hasattr(lookup_field, 'field'):
                    # this step is needed for backwards relations
                    lookup_field = lookup_field.field
            except FieldDoesNotExist:
                parts.pop()
                break

            try:
                lookup_model = lookup_field.rel.to
            except AttributeError:
                parts.pop()
                break

        node.field = (lookup_model._meta.db_table, lookup_field.attname)
    node.field = node.field + (alias,)
