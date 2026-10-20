from .menu import get_menu


def sidebar_menu(request):
    if request.path.startswith('/back/'):
        return {'sidebar_menu': get_menu('backend_menu.json', request.user), 'menu_scope': 'back'}
    if request.path.startswith('/front/'):
        return {'sidebar_menu': get_menu('frontend_menu.json', request.user), 'menu_scope': 'front'}
    return {}
