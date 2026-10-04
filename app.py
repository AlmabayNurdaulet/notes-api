#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

notes = {}


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        # Health check
        if self.path == '/healthz':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            return

        # List all notes
        if self.path == '/':
            self._send_json(200, {'notes': list(notes.values())})
            return

        # Get one note by id
        if self.path.startswith('/notes/'):
            note_id = self.path.split('/')[-1]
            if note_id in notes:
                self._send_json(200, notes[note_id])
                return
            self._send_json(404, {'error': 'not found'})
            return

        self._send_json(404, {'error': 'not found'})

    def do_POST(self):
        # Create a note
        if self.path == '/notes':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else b'{}'
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._send_json(400, {'error': 'invalid json'})
                return
            note_id = str(len(notes) + 1)
            notes[note_id] = {'id': note_id, 'text': data.get('text', '')}
            self._send_json(201, notes[note_id])
            return

        self._send_json(404, {'error': 'not found'})

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'Starting on port {port}')
    server.serve_forever()
