import colander

from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound
    )

from pyramid.view import (
    view_config,
    forbidden_view_config
    )
from pyramid.security import (
    remember,
    NO_PERMISSION_REQUIRED,
    )

from pyramid_zodbconn import get_connection
from pyramid.session import check_csrf_token

from substanced.sdi import (
    mgmt_view,
    )

from substanced.schema import Schema
from substanced.util import (
    oid_of,
    find_content,
    find_service,
    )
from substanced.form import FormView

from velruse import login_url as velruse_login_url

class TeamsView(object):
    subnav_items = []
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @forbidden_view_config(renderer='templates/login.pt')
    @view_config(name='login', renderer='templates/login.pt')
    @mgmt_view(name='login', renderer='templates/login.pt',
               tab_condition=False)
    @mgmt_view(renderer='templates/login.pt', context=HTTPForbidden,
               tab_condition=False)
    def login(self):
        request = self.request
        context = self.context
        request.layout_manager.use_layout('simple')

        login_url = request.mgmt_path(request.context, 'login')
        referrer = request.url
        if login_url in referrer: # pragma: no cover
            # never use the login form itself as came_from
            referrer = request.mgmt_path(request.root)
        came_from = request.session.setdefault('came_from', referrer)

        # XXX TODO Overrule this
        came_from = request.resource_url(request.root)

        login = ''
        password = ''
        if 'form.submitted' in request.params:
            try:
                check_csrf_token(request)
            except:
                request.session.flash('Failed login (CSRF)', 'error')
            else:
                login = request.params['login']
                password = request.params['password']
                principals = find_service(context, 'principals')
                users = principals['users']
                user = users.get(login)
                if user is not None and user.check_password(password):
                    headers = remember(request, oid_of(user))
                    request.session.flash('Welcome!', 'success')
                    return HTTPFound(location=came_from, headers=headers)
                request.session.flash('Failed login', 'error')

        return dict(
            heading='Fastbreak Login',
            url=request.mgmt_path(request.root, 'login'),
            came_from=came_from,
            login=login,
            password=password,
            login_url=velruse_login_url,
            providers=request.registry.settings[
                      'substanced.login_providers']
        )


@view_config(context='velruse.AuthenticationComplete')
def external_login_complete(request):
    profile = request.context.profile
    came_from = request.session.get('came_from', request.application_url)
    site_root = find_content(request.context, 'Root')
    principals = find_service(site_root, 'principals')
    users = principals['users']
    display_name = profile['displayName'].lower()
    user = [user for user in users.values() if user.__name__ ==
                                               display_name]
    if not user:
        request.session['twitter_name'] = display_name
        return HTTPFound(request.resource_url(site_root, 'register_user'))
        ## fmt = 'Twitter user "%s" is not setup in Fastbreak'
        ## request.session.flash(fmt % profile['displayName'])
        # return external_login_denied(request)
    headers = remember(request, oid_of(user[0]))
    request.session.flash('Welcome!', 'success')

    # XXX TODO Overrule this
    came_from = '/'
    return HTTPFound(location=came_from, headers=headers)

@view_config(context='velruse.AuthenticationDenied')
def external_login_denied(request):
    request.layout_manager.use_layout('simple')
    connection = get_connection(request)
    site_root = connection.root()['app_root']
    login_url = request.mgmt_path(site_root, 'login')
    return HTTPFound(location=login_url)




@colander.deferred
def deferred_twitter_name_default(node, kw):
    request = kw['request']
    twitter_name = request.session.get('twitter_name', '')
    def twitter_name_default(node, val):
        return twitter_name
    return twitter_name_default

class LoginName(colander.SchemaNode):
    schema_type = colander.String

    @property
    def default(self):
        request = self.bindings['request']
        twitter_name = request.session.get('twitter_name', '')
        return twitter_name

    def validator(self, node, val):
        if 'group.' in val:
            raise colander.Invalid('Login name must not contain group.')

class RegisterUserSchema(Schema):
    login = LoginName()
    
    email = colander.SchemaNode(
        colander.String(),
        validator=colander.Email(),
        )

@view_config(
    name='register_user',
    permission=NO_PERMISSION_REQUIRED, 
    renderer='templates/form.pt',
    )
class RegisterUserView(FormView):
    title = 'Add User'
    schema = RegisterUserSchema()
    buttons = ('register',)

    def register_success(self, appstruct):
        login = appstruct['login']
        email = appstruct['email']
        pservice = find_service(self.context, 'principals')
        pservice.add_user(login, email=email)
        return HTTPFound(
            self.request.sdiapi.mgmt_path(self.context, 'awaiting_approval')
            )


def includeme(config): # pragma: no cover
    settings = config.registry.settings
    providers = settings.get('substanced.login_providers', '')
    providers = filter(None, [p.strip()
                              for line in providers.splitlines()
                              for p in line.split(', ')])
    settings['substanced.login_providers'] = providers
    if 'github' in providers:
        config.include('velruse.providers.github')
        config.add_github_login_from_settings(prefix='github.')
    if 'twitter' in providers:
        config.include('velruse.providers.twitter')
        config.add_twitter_login_from_settings(prefix='twitter.')
    if 'google' in providers:
        config.include('velruse.providers.google')
        config.add_google_login(
            realm=settings['google.realm'],
            consumer_key=settings['google.consumer_key'],
            consumer_secret=settings['google.consumer_secret'],
        )
    if 'yahoo' in providers:
        config.include('velruse.providers.yahoo')
        config.add_yahoo_login(
            realm=settings['yahoo.realm'],
            consumer_key=settings['yahoo.consumer_key'],
            consumer_secret=settings['yahoo.consumer_secret'],
        )
