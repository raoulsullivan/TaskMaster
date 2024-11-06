from enum import Enum
import re


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"


class RouteNotFound(Exception):
    def __init__(self, url, message="Route not found"):
        self.url = url
        self.message = f"{message}: URL {url}"
        super().__init__(self.message)


class MethodNotAllowed(Exception):
    def __init__(self, url, method, message="Method not allowed"):
        self.method = method
        self.url = url
        self.message = f"{message}: {method} for URL {url}"
        super().__init__(self.message)


class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, path, handler, method):
        # Convert path parameters (e.g., /users/<id>) to regex
        param_pattern = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", path)
        path_regex = re.compile(f"^{param_pattern}$")
        self.routes.append((path_regex, handler, method))

    def match(self, url_path, method):
        matching_routes_by_url = []
        # First identify the matching URLs
        for path_regex, handler, route_method in self.routes:
            match = path_regex.match(url_path)
            if match:
                params = match.groupdict()
                matching_routes_by_url.append((handler, route_method, params))
        if not matching_routes_by_url:
            raise RouteNotFound(url_path)

        # Then check the method is allowed
        for matching_route in matching_routes_by_url:
            handler, route_method, params = matching_route
            if route_method.value == method.upper():
                return handler, params
        raise MethodNotAllowed(url_path, method)
