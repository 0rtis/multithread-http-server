#!/usr/bin/env python
"""
MIT License

Copyright (c) 2018 Ortis (cao.ortis.org@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from multithread_http_server import MultiThreadHttpServer
from http.server import BaseHTTPRequestHandler
import threading
import time
import logging


class HTTPStreamHandler(BaseHTTPRequestHandler):

	def log_message(self, format, *args):
		return  # silence log

	def do_GET(self):
		self.server.request_callback('GET', self)

	def do_POST(self):
		self.server.request_callback('POST', self)


def stream_forever(http_method, stream_handler):

	if http_method == 'GET':
		stream_handler.send_response(200)
		stream_handler.send_header('Content-type', 'text/html')
		stream_handler.end_headers()
		stream_handler.wfile.write(
			bytes(str(threading.current_thread().getName()) + " is counting<br><br>", 'utf-8'))

		""" Stream until stopped """
		i = 0
		while not stream_handler.server.stop_requested:
			time.sleep(1)
			i = i + 1
			stream_handler.wfile.write(bytes(str(i) + " ", 'utf-8'))
	else:
		stream_handler.send_response(404)


if __name__ == '__main__':

	logging.basicConfig(level=logging.DEBUG)
	server = MultiThreadHttpServer(('', 80), 5, HTTPStreamHandler, request_callback=stream_forever, log=logging.getLogger("multi thread server"))
	server.start(background=True)  # background=True for non blocking
	time.sleep(30)  # let the server run a while
	print("Requesting stop")
	server.stop()
	print("Stopped")

