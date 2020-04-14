import datetime
from django import template

register = template.Library()


@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)


@register.inclusion_tag('common/nav-element.html', takes_context=True)
def create_nav_link(context, link_path, link_text):
    return {
        'request_path': context['request'].path,
        'path': link_path,
        'text': link_text,
    }
