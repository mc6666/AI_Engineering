from django import template

register = template.Library()


@register.inclusion_tag('partials/menu_tree.html')
def render_menu(nodes):
    return {'nodes': nodes}
