
from substanced.root import Root
from substanced.event import (
    subscribe_created,
    )


@subscribe_created(Root)
def root_created(event):
#    catalogs = find_service(event.object, 'catalogs')
#    catalogs.add_catalog('sdidemo', update_indexes=True)
#    add_sample_content(event.object, event.registry)
    return


