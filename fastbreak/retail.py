from pyramid.url import resource_url
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

    @property
    def documents(self):
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(IDocument,))
        return [resolver(docid) for docid in docids]

    @property
    def topics(self):
        search_catalog = self.request.search_catalog
        count, docids, resolver = search_catalog(interfaces=(ITopic,))
        return [resolver(docid) for docid in docids]

    @view_config(renderer='templates/siteroot_view.pt',
                 context=ISite)
    def siteroot_view(self):
        return dict(title='Welcome to My Site')

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

        return dict(title='My Documents', documents=documents)

    @view_config(renderer='templates/document_view.pt',
                 context=IDocument)
    def document_view(self):
        self.title = self.context.title

        objectid = -1099536351
        from substanced.service import find_service

        objectmap = find_service(self.context, 'objectmap')
        topic = objectmap.object_for(objectid)

        return dict(title=self.context.title,
                    body=self.context.body,
                    topic=topic)

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

        return dict(title='My Topics', topics=topics)

    @view_config(renderer='templates/topic_view.pt',
                 context=ITopic)
    def topic_view(self):
        documents = self.documents

        # TODO this is just temporary until I wire up widget
        from substanced.util import oid_of

        oid = oid_of(self.context)

        return dict(title=self.context.title,
                    oid=oid,
                    documents=documents)

