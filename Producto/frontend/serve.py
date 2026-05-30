"""Servidor HTTP sin caché — todos los archivos se sirven con no-store."""
import os, http.server, socketserver

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    def log_message(self, fmt, *args):
        pass  # silenciar logs

os.chdir(r'c:\Users\prueba\Downloads\Trato_Hecho-main\Trato_Hecho-main')
with socketserver.TCPServer(('127.0.0.1', 9000), NoCacheHandler) as httpd:
    print('Serving (no-cache) at http://127.0.0.1:9000')
    httpd.serve_forever()
