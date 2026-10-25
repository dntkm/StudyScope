"""Preview web/ with the real learning archive on localhost."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
import argparse
import json
from build import ROOT, create_version


class Handler(SimpleHTTPRequestHandler):
    def target(self):
        path = unquote(urlsplit(self.path).path).lstrip('/')
        if path.startswith('learning/'):
            base, relative = ROOT / 'learning', path[len('learning/'):]
        else:
            base, relative = ROOT / 'web', path or 'index.html'
        target = (base / relative).resolve()
        if not target.is_relative_to(base.resolve()):
            raise ValueError('Path must stay inside the public page or archive')
        return target

    def translate_path(self, path):
        return str(self.target())

    def do_GET(self):
        if urlsplit(self.path).path == '/version.json':
            content = json.dumps(create_version('preview')).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            super().do_GET()

    def send_head(self):
        try:
            if not self.target().is_file():
                self.send_error(404)
                return None
        except ValueError:
            self.send_error(404)
            return None
        return super().send_head()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(ROOT / 'web')))
    print(f'StudyScope: http://127.0.0.1:{server.server_port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
