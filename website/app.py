
""" This contains the entry point for the gunicorn server (app)
and registers the controller functions with the router.
"""
from jinja2 import Environment, FileSystemLoader

from taskmaster.taskmaster import get_tasks
from website.router import HTTPMethod, Router, MethodNotAllowed, RouteNotFound
from website.htmlresponse import HTMLResponse, HTTPStatus

env = Environment(loader=FileSystemLoader('website/templates'))


def handle_request(environ):
    """Responsible for calling the handler function"""
    url_path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD')
    handler, params = router.match(url_path, method)
    return handler(**params)


def app(environ, start_response):
    """Entry point to the web application
    Responsible for getting a Response and passing it to Gunicorn"""
    try:
        response = handle_request(environ)
    except RouteNotFound as e:
        template = env.get_template('error.html')
        html_output = template.render({'error_message': e})
        response = HTMLResponse(body=html_output,
                                status_code=HTTPStatus.NOT_FOUND)
    except MethodNotAllowed as e:
        template = env.get_template('error.html')
        html_output = template.render({'error_message': e})
        response = HTMLResponse(body=html_output,
                                status_code=HTTPStatus.METHOD_NOT_ALLOWED)
    except Exception as e:
        # Yes, we do want to catch all other exceptions here
        # otherwise we just get the default Nginx Internal Server Error page
        template = env.get_template('error.html')
        html_output = template.render({'error_message': e})
        response = HTMLResponse(body=html_output,
                                status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    headers = [(k, v) for k, v in response.headers.items()]
    start_response(response.status_code.value, headers)
    return [response.body]


def hello():
    template = env.get_template('hello.html')
    tasks = get_tasks()
    data = {'tasks': tasks}
    html_output = template.render(data)
    return HTMLResponse(body=html_output)


router = Router()
router.add_route("/", hello, HTTPMethod.GET)
