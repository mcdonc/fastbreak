import unittest
from pyramid import testing

class Test_griddemo_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from views import griddemo_view
        return griddemo_view(context, request)

    def test_it(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        result = self._callFUT(context, request)
        self.assertEqual(result['heading'], 'Grid Demo')
