from functools import lru_cache
from django.utils.functional import cached_property
from django.test.signals import setting_changed


class FieldRender(object):
    def __init__(self, bound_field):
        self.bound_field = bound_field

    @property
    def field(self):
        return self.bound_field.field

    @property
    def widget(self):
        return self.field.widget

    @property
    def disabled(self):
        return self.field.disabled

    @property
    def required(self):
        return (
            self.widget.use_required_attribute(self.bound_field.initial) and
            self.field.required and
            self.bound_field.form.use_required_attribute
        )

    @cached_property
    def value(self):
        return self.bound_field.value()

    @cached_property
    def formatted_value(self):
        return self.widget.format_value(self.value)

    @cached_property
    def errors(self):
        return self.bound_field.errors

    def __str__(self):
        return str(self.bound_field)


@lru_cache(maxsize=None)
def get_field_renderer(field):
    from material.settings import material_settings

    for field_class in type(field).mro()[:-2]:
        if field_class in material_settings.FIELD_RENDERERS:
            return material_settings.FIELD_RENDERERS[field_class]

    for widget_class in type(field.widget).mro()[:-2]:
        if widget_class in material_settings.WIDGET_RENDERERS:
            return material_settings.WIDGET_RENDERERS[widget_class]

    return FieldRender


def _clear_field_renderer_cache(*args, **kwargs):
    if kwargs['setting'] == 'MATERIAL':
        get_field_renderer.cache_clear()


setting_changed.connect(_clear_field_renderer_cache)