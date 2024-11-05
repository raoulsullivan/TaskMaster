from enum import Enum


class HTTPStatus(Enum):
    OK = "200 OK"
    NOT_FOUND = "404 Not Found"


class HTMLResponse:
    def __init__(self, body='', status_code=HTTPStatus.OK, headers=None,
                 content_type='text/html', encoding='utf-8'):
        self.body = body.encode(encoding) if isinstance(body, str) else body
        self.status_code = status_code
        self.headers = headers or {}
        self.headers['Content-Type'] = content_type
        self.encoding = encoding

        if 'Content-Length' not in self.headers:
            self.headers['Content-Length'] = str(len(self.body))
