import json
from pathlib import Path

from django.conf import settings
from django.urls import NoReverseMatch, reverse


def _load_menu_file(filename):
    path = Path(settings.BASE_DIR) / 'static' / 'data' / filename
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _user_function_codes(user):
    """Returns the set of function codes the user may see, or None if unrestricted."""
    if not user.is_authenticated:
        return set()
    if user.is_superuser:
        return None
    from accounts.models import Function
    return set(Function.objects.filter(roles__users=user).values_list('code', flat=True))


def _build_node(node, allowed_codes):
    code = node.get('function_code')
    if allowed_codes is not None and code and code not in allowed_codes:
        return None

    children = []
    for child in node.get('children', []):
        built = _build_node(child, allowed_codes)
        if built:
            children.append(built)

    if allowed_codes is not None and code is None and not children and not node.get('url_name'):
        return None

    url = '#'
    if node.get('url_name'):
        try:
            url = reverse(node['url_name'])
        except NoReverseMatch:
            url = '#'

    return {
        'title': node['title'],
        'icon': node.get('icon', ''),
        'url': url,
        'children': children,
    }


def get_menu(filename, user):
    allowed_codes = _user_function_codes(user)
    tree = _load_menu_file(filename)
    menu = []
    for node in tree:
        built = _build_node(node, allowed_codes)
        if built:
            menu.append(built)
    return menu
