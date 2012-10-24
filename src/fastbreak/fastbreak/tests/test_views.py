import os.path
import tempfile
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


class FunctionalTests(unittest.TestCase):
    viewer_login = '/login?login=viewer&password=viewer'\
                   '&came_from=FrontPage&form.submitted=Login'
    viewer_wrong_login = '/login?login=viewer&password=incorrect'\
                         '&came_from=FrontPage&form.submitted=Login'
    editor_login = '/login?login=editor&password=editor'\
                   '&came_from=FrontPage&form.submitted=Login'

    def setUp(self):
        # Make a fake database place
        from fastbreak import main

        self.tmpdir = tempfile.mkdtemp()
        dbpath = os.path.join(self.tmpdir, 'test.db')
        db_uri = 'file://' + dbpath
        global_config = {'zodbconn.uri': db_uri}

        # Simulate the INI file
        settings = {
            'substanced.secret': 'seekri1',
#            'substanced.uploads_tempdir':
# '/Users/paul/projects/fastbreak/etc/../var/tmp',
            'zodbconn.uri': db_uri,
            'pyramid.includes': 'pyramid_tm pyramid_exclog pyramid_layout'
        }


        # Open the "main" function, let's get started
        from fastbreak import main

        app = main(global_config, **settings)

        # Now we're ready
        from webtest import TestApp

        self.testapp = TestApp(app)


    def tearDown(self):
        import shutil

        #self.db.close()
        shutil.rmtree(self.tmpdir)

    def test_root(self):
        res = self.testapp.get('/login', status=200)
        self.assertTrue('Fastbreak Account' in res.body)

    def xsetUp(self):
        from fastbreak import main

        settings = {
            'substanced.secret': 'seekri1',
            'substanced.uploads_tempdir': '/Users/paul/projects/fastbreak/etc/../var/tmp',
            'zodbconn.uri': 'zeo://localhost:9993?cache_size=200MB&blob_dir=/Users/paul/projects/fastbreak/etc/../var/blobs&shared_blob_dir=true&storage=main',
            'pyramid.includes': 'pyramid_tm pyramid_exclog pyramid_layout'
        }

        app = main({}, **settings)
        self.testapp = TestApp(app)

    def xtest_it(self):
        res = self.testapp.get('/login', status=200)
        self.assertTrue('Fastbreak Account' in res.body)