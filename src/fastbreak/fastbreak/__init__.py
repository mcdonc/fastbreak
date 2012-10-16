from pyramid.config import Configurator

from substanced import root_factory

def main(global_config, **settings):
    config = Configurator(settings=settings, root_factory=root_factory)
    config.add_static_view('static', 'fastbreak:static')
    config.include('substanced')
    config.include('.auth')
    config.scan()
    return config.make_wsgi_app()
