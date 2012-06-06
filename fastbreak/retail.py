from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget
    )
from pyramid.view import view_config, forbidden_view_config

from substanced.site import ISite
from substanced.service import find_service
from substanced.util import oid_of

from .layout import Layout

class SplashView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(renderer='templates/siteroot_view.pt',
                 permission='view',
                 context=ISite)
    def siteroot_view(self):
        return dict(heading='Welcome to My Site')


    @view_config(context=ISite, name='login',
                 renderer='templates/login.pt')
    @forbidden_view_config(renderer='templates/login.pt')
    def login(self):
        request = self.request
        login_url = request.resource_url(request.context, 'login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/' # never use the login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            principals = find_service(self.context, 'principals')
            users = principals['users']
            user = users.get(login)

            if user is not None and user.check_password(password):
                headers = remember(self.request, oid_of(user))
                request.session.flash('Welcome!', 'success')
                return HTTPFound(location = came_from, headers = headers)
            message = 'Failed login'

        return dict(
            heading='Login',
            message=message,
            url=request.application_url + '/login',
            came_from=came_from,
            login=login,
            password=password,
            )

    @view_config(context=ISite, name='logout')
    def logout(self):
        request = self.request
        headers = forget(request)
        return HTTPFound(location=request.resource_url(request.context),
                         headers=headers)