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


import socket
import threading
import time
from http.server import HTTPServer
import logging


class MultiThreadHttpServer:

	def __init__(self, host, parallelism, http_handler_class, request_callback=None, log=None):
		"""
		:param host: host to bind. example: '127.0.0.1:80'
		:param parallelism: number of thread listener and backlog
		:param http_handler_class: the handler class extending BaseHTTPRequestHandler
		:param request_callback: callback on incoming request. This method can be accede in the HTTPHandler instance.
				Example: self.server.request_callback(
														'GET',  # specify http method
														self  # pass the HTTPHandler instance
													)
		"""

		self.host = host
		self.parallelism = parallelism
		self.http_handler_class = http_handler_class
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.request_callback = request_callback
		self.connection_handlers = []
		self.stop_requested = False
		self.log = log

	def start(self, background=False):
		self.socket.bind(self.host)
		self.socket.listen(self.parallelism)

		if self.log is not None:
			self.log.debug("Creating "+str(self.parallelism)+" connection handler")

		for i in range(self.parallelism):
			ch = ConnectionHandler(self.socket, self.http_handler_class, self.request_callback)
			ch.start()
			self.connection_handlers.append(ch)

		if background:
			if self.log is not None:
				self.log.debug("Serving (background thread)")
			threading.Thread(target=self.__serve).start()
		else:
			if self.log is not None:
				self.log.debug("Serving (current thread)")
			self.__serve()

	def stop(self):
		self.stop_requested = True
		for ch in self.connection_handlers:
			ch.stop()

	def __serve(self):
		"""
		Serve until stop() is called. Blocking method
		:return:
		"""
		while not self.stop_requested:
			time.sleep(1)


class ConnectionHandler(threading.Thread, HTTPServer):

	def __init__(self, sock, http_handler_class, request_callback=None):
		HTTPServer.__init__(self, sock.getsockname(), http_handler_class, False)
		self.socket = sock
		self.server_bind = self.server_close = lambda self: None
		self.HTTPHandler = http_handler_class
		self.request_callback = request_callback

		threading.Thread.__init__(self)
		self.daemon = True
		self.stop_requested = False

	def stop(self):
		self.stop_requested = True

	def run(self):
		""" Each thread process request forever"""
		self.serve_forever()

	def serve_forever(self):
		""" Handle requests until stopped """
		while not self.stop_requested:
			self.handle_request()

		print("Finish" + str(threading.current_thread()))

