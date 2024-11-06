
""" This contains the entry point for the gunicorn server (app)
and registers the controller functions with the router.
"""
from jinja2 import Environment, FileSystemLoader
from urllib.parse import parse_qs

from taskmaster.taskmaster import execute_task, get_tasks
from website.router import HTTPMethod, Router, MethodNotAllowed, RouteNotFound
from website.htmlresponse import HTMLResponse, HTTPStatus

env = Environment(loader=FileSystemLoader('website/templates'))


def handle_request(environ):
    """Responsible for calling the handler function"""
    url_path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD')
    handler, params = router.match(url_path, method)
    return handler(environ, **params)


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


def _get_form_data(environ):
    """Used to parse a form"""
    if environ['REQUEST_METHOD'] != 'POST':
        raise Exception('Only works on POSTS!')
    content_type = environ.get('CONTENT_TYPE', None)
    if content_type != 'application/x-www-form-urlencoded':
        raise Exception(f'Unexpected content type {content_type}')

    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        content_length = 0

    form_data = environ['wsgi.input'].read(content_length)
    return parse_qs(form_data.decode('utf-8'))


def hello(environ):
    template = env.get_template('hello.html')
    tasks = get_tasks()
    data = {'tasks': tasks}
    html_output = template.render(data)
    return HTMLResponse(body=html_output)


def execute(environ):
    template = env.get_template('execute.html')
    tasks = get_tasks()
    data = {'tasks': tasks}
    html_output = template.render(data)
    return HTMLResponse(body=html_output)


def execute_post(environ):
    form_data = _get_form_data(environ)
    executed_task_id = form_data['task_id'][0]
    execution = execute_task(executed_task_id)
    template = env.get_template('execution_successful.html')
    data = {'execution': execution}
    html_output = template.render(data)
    return HTMLResponse(body=html_output)


router = Router()
router.add_route("/", hello, HTTPMethod.GET)
router.add_route("/tasks/execute", execute, HTTPMethod.GET)
router.add_route("/tasks/execute", execute_post, HTTPMethod.POST)
