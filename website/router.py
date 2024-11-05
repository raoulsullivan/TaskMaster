import re


class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, path, handler):
        # Convert path parameters (e.g., /users/<id>) to regex
        param_pattern = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", path)
        path_regex = re.compile(f"^{param_pattern}$")
        self.routes.append((path_regex, handler))

    def match(self, url_path):
        for path_regex, handler in self.routes:
            match = path_regex.match(url_path)
            if match:
                # Extract parameters and call the handler with them
                params = match.groupdict()
                return handler, params
        return None, None
