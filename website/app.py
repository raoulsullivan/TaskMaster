
""" This contains the entry point for the gunicorn server (app)
and registers the controller functions with the router.
"""
from jinja2 import Environment, FileSystemLoader

from taskmaster.taskmaster import get_tasks
from website.router import Router
from website.htmlresponse import HTMLResponse, HTTPStatus

env = Environment(loader=FileSystemLoader('website/templates'))


def handle_request(url_path):
    """Responsible for calling the handler function"""
    handler, params = router.match(url_path)
    if handler:
        return handler(**params)
    else:
        raise RouteNotFound(url_path)


def app(environ, start_response):
    """Entry point to the web application
    Responsible for getting a Response and passing it to Gunicorn"""
    path = environ.get('PATH_INFO', '')
    try:
        response = handle_request(path)
    except RouteNotFound:
        template = env.get_template('not_found.html')
        html_output = template.render()
        response = HTMLResponse(body=html_output,
                                status_code=HTTPStatus.NOT_FOUND)

    headers = [(k, v) for k, v in response.headers.items()]
    start_response(response.status_code.value, headers)
    return [response.body]


class RouteNotFound(Exception):
    def __init__(self, url, message="Route not found"):
        self.url = url
        self.message = f"{message}: URL {url}"
        super().__init__(self.message)


def hello():
    template = env.get_template('hello.html')
    tasks = get_tasks()
    data = {'tasks': tasks}
    html_output = template.render(data)
    return HTMLResponse(body=html_output)


router = Router()
router.add_route("/", hello)
