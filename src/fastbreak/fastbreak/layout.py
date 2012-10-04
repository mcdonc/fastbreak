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
    def navbar_items(self):
        # Get the teams and sort them by order of "position"
        request = self.request
        context_name = self.context.__name__

        teams = []
        sorted_teams = sorted(request.root['teams'].values(),
                              key=lambda x: x.props['position'])
        for team in sorted_teams:
            active = ''
            if context_name==team.__name__:
                active='active'
            teams.append(dict(
                title=team.title,
                url=request.resource_url(team),
                active=active
            ))
        return teams

    @property
    def project_title(self):
        return 'Pyramid Layout App!'
