from pyramid.decorator import reify
from pyramid.renderers import get_renderer
from pyramid.url import resource_url

class Layout(object):
    heading = 'No Assigned Title'

    @reify
    def macros(self):
        fn = 'templates/global_layout.pt'
        template = get_renderer(fn).implementation()
        return {'layout': template}

    @reify
    def manage_prefix(self):
        settings = self.request.registry.settings
        return settings.get('substanced.manage_prefix',
                            '/manage')

    def find_interface(self, interface):
        """Find all content matching an interface"""
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(
            interfaces=(interface,),
            sort_index=('title'),
        )
        results = [resolver(docid) for docid in docids]

        return results

    def make_url(self, resource):
        """From ZPT, given a resource, make a URL"""

        return resource_url(resource, self.request)