# -*- coding: utf-8 -*-
from django.db.models import QuerySet, Manager, Model, BooleanField, DateTimeField


class LogicDeleteQueryset(QuerySet):
    def delete(self):
        self.update(is_delete=True)

    def phys_delete(self):
        return super(LogicDeleteQueryset, self).delete()


class LogicDeleteManager(Manager):
    def get_queryset(self):
        return LogicDeleteQueryset(self.model, using=self._db)

    def all(self):
        queryset = self.get_queryset()
        return queryset.filter(is_delete=False)

    def items_all(self):
        return self.get_queryset()


class LogicDeleteModel(Model):
    is_delete = BooleanField(default=False, verbose_name='是否已删除')
    objects = LogicDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_delete = True
        self.save()

    def recover(self):
        self.is_delete = False
        self.save()

    def phys_delete(self, using=None):
        return super(LogicDeleteModel, self).delete(using)


class TimeMarkModel(Model):
    created_at = DateTimeField(auto_now=True, verbose_name='创建时间')
    updated_at = DateTimeField(auto_now=True, verbose_name='修改时间')

    class Meta:
        abstract = True


