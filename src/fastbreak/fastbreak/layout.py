from pyramid_layout.layout import layout_config


@layout_config(
    template='templates/layout.pt'
)
class FastbreakLayout(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url
        self.headings = []

    @property
    def project_title(self):
        return 'Pyramid Layout App!'
