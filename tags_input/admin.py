from django.contrib import admin

from . import fields
from . import widgets


class TagsInputMixin(object):
    def get_tag_fields(self):
        '''Get a list fo fields on this model that could be potentially tagged.

        By default reads self.tag_fields if it exists of returns None for
        default behavious.
        '''

        return getattr(self, 'tag_fields', None)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        '''
        Get a form Field for a ManyToManyField.
        '''
        
        try:
            rel = db_field.rel
        except AttributeError:
            rel = db_field.remote_field
 
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        if not rel.through._meta.auto_created:
            return None
        
        try:
            to = rel.to
        except AttributeError:
            to = rel.model

        # If there is a list of taggable fields, and this filed isn't one of
        # them, then fall back to parent method.
        tag_fields = self.get_tag_fields()

        if tag_fields and db_field.name not in tag_fields:
            print('in fields', tag_fields, db_field.name)
            return super(TagsInputMixin, self).formfield_for_manytomany(
                db_field, request, **kwargs)
        else:
            print('nin fields', tag_fields, db_field.name)

        queryset = to._default_manager.get_queryset()

        kwargs['queryset'] = queryset
        kwargs['widget'] = widgets.AdminTagsInputWidget(
            verbose_name=db_field.verbose_name,
            is_stacked=db_field.name in self.filter_vertical,
            attrs=kwargs.get('attrs'),
            choices=kwargs.get('choices', ()), )
        kwargs['required'] = not db_field.blank
        kwargs['help_text'] = getattr(db_field, 'help_text', None)
        kwargs['verbose_name'] = getattr(db_field, 'verbose_name', None)

        # Ugly hack to stop the Django admin from adding the + icon

        if db_field.name not in self.raw_id_fields:
            self.raw_id_fields = list(self.raw_id_fields)
            self.raw_id_fields.append(db_field.name)

        return fields.AdminTagsInputField(**kwargs)


class TagsInputAdmin(TagsInputMixin, admin.ModelAdmin):
    pass


class TagsInputTabularInline(TagsInputMixin, admin.TabularInline):
    pass


class TagsInputStackedInline(TagsInputMixin, admin.StackedInline):
    pass


