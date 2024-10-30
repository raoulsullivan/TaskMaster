from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))


def app(environ, start_response):
    template = env.get_template('hello.html')
    content = 'Hello, World, this is TaskMaster!'
    data = {'content': content}
    html_output = template.render(data)
    byte_output = html_output.encode("utf-8")
    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    return [byte_output]
