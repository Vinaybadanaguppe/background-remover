#!/usr/bin/env python3
"""
Ultra-simple server that binds to port immediately
"""
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

PORT = int(os.environ.get('PORT', 10000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "Simple server is running",
                "port": str(PORT)
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == '__main__':
    print(f"🚀 STARTING SIMPLE SERVER ON 0.0.0.0:{PORT}")
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"✅ SERVER BOUND TO PORT {PORT}")
    server.serve_forever()
