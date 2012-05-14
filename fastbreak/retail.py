from pyramid.url import resource_url
from pyramid.decorator import reify
from pyramid.view import view_config

from substanced.site import ISite

from .interfaces import (
    IDocument,
    ITeam
    )
from .layout import Layout


class SplashView(Layout):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @reify
    def documents(self):
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(IDocument,))
        return [resolver(docid) for docid in docids]

    @reify
    def all_teams(self):
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(ITeam,))
        return [resolver(docid) for docid in docids]

    @view_config(renderer='templates/siteroot_view.pt',
                 context=ISite)
    def siteroot_view(self):
        return dict(heading='Welcome to My Site')

    @view_config(renderer='templates/documents_list.pt',
                 name='documents',
                 context=ISite)
    def documents_list(self):
        documents = []
        for document in self.documents:
            documents.append(
                    {'url': resource_url(document,
                                         self.request),
                     'title': document.title,
                     })

        return dict(heading='My Documents', documents=documents)

    @view_config(renderer='templates/document_view.pt',
                 context=IDocument)
    def document_view(self):
        return dict(heading=self.context.title,
                    body=self.context.body,
                    teams=self.context.teams())

    @view_config(renderer='templates/teams_list.pt',
                 name='teams',
                 context=ISite)
    def teams_list(self):
        teams = []
        for team in self.all_teams:
            teams.append(
                    {'url': resource_url(team,
                                         self.request),
                     'title': team.title,
                     })

        return dict(heading='My Teams', teams=teams)

    @view_config(renderer='templates/team_view.pt',
                 context=ITeam)
    def team_view(self):
        return dict(heading=self.context.title,
                    documents=self.context.documents())

