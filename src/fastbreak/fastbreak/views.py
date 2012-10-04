from pyramid.view import view_config

@view_config(name="griddemo", renderer="templates/demo76.pt")
def griddemo_view(request):
    return {}
