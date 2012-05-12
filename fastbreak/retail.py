from pyramid.url import resource_url
from pyramid.decorator import reify
from pyramid.view import view_config

from substanced.site import ISite

from .interfaces import (
    IDocument,
    ITopic
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
    def topics(self):
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(ITopic,))
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
                    topics=self.context.topics())

    @view_config(renderer='templates/topics_list.pt',
                 name='topics',
                 context=ISite)
    def topics_list(self):
        topics = []
        for topic in self.topics:
            topics.append(
                    {'url': resource_url(topic,
                                         self.request),
                     'title': topic.title,
                     })

        return dict(heading='My Topics', topics=topics)

    @view_config(renderer='templates/topic_view.pt',
                 context=ITopic)
    def topic_view(self):
        return dict(heading=self.context.title,
                    documents=self.context.documents())

