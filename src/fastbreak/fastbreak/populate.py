"""Bulk load test/migration data"""

import os
import logging
import sys

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )

import transaction

from substanced.folder import Folder

def main(argv=sys.argv):
    if len(argv) != 2:
        cmd = os.path.basename(argv[0])
        print 'usage: %s <config_uri>\n' % cmd
        sys.exit()

    config_uri = argv[1]
    setup_logging(config_uri)
    log = logging.getLogger(__name__)
    env = bootstrap(config_uri)
    root = env['root']

    # relative paths

    # assumes root['splash_pages'] was initialized in Site
    log.info('Adding top-level folders...')
    with transaction.manager:
        team = Folder()
        root['teams'] = team

if __name__ == '__main__':
    main()
