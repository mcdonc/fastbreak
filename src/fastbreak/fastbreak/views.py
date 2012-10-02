from pyramid.view import view_config

@view_config(renderer="templates/hello.pt")
def hello_view(request):
    return {"tutorial": "Little Dummy"}

@view_config(name="griddemo", renderer="templates/demo76.pt")
def griddemo_view(request):
    return {}
