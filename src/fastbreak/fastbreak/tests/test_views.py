import unittest
from pyramid import testing
from webtest import TestApp

class Test_site_view(unittest.TestCase):
    def _makeOne(self, context, request):
        from fastbreak.views import SiteView
        return SiteView(context, request)

    def test_it(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()

        inst = self._makeOne(context, request)
        res = inst.site_view()
        self.assertEqual(res['heading'], 'Fastbreak')

class FTest_site_view(unittest.TestCase):
    def setUp(self):
        from fastbreak import main
        config = {
            'substanced.secret': '',
        }
        app = main({}, **config)
        self.testapp = TestApp(app)

    def test_it(self):
        res = self.testapp.get('/', status=200)
        self.failUnless('Login' in res.body)