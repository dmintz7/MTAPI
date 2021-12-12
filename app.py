# coding: utf-8
"""
	mta-api-sanity
	~~~~~~

	Expose the MTA's real-time subway feed as a json api

	:copyright: (c) 2014 by Jon Thornton.
	:license: BSD, see LICENSE for more details.
"""

from mtapi.mtapi import Mtapi
from flask import Flask, request, jsonify, render_template, abort, redirect
from flask.json import JSONEncoder
from datetime import datetime
from functools import wraps, reduce
import logging, os, sys

app = Flask(__name__)


formatter = logging.Formatter('%(asctime)s - %(levelname)10s - %(module)15s:%(funcName)30s:%(lineno)5s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
logger.setLevel(os.environ['LOG_LEVEL'])
logging.getLogger("requests").setLevel(logging.WARNING)

class CustomJSONEncoder(JSONEncoder):

	def default(self, obj):
		try:
			if isinstance(obj, datetime):
				return obj.isoformat()
			iterable = iter(obj)
		except TypeError:
			pass
		else:
			return list(iterable)
		return JSONEncoder.default(self, obj)
app.json_encoder = CustomJSONEncoder

mta = Mtapi(
	os.environ['MTA_KEY'],
	os.environ['STATIONS_FILE'],
	max_trains=os.environ['MAX_TRAINS'],
	max_minutes=os.environ['MAX_MINUTES'],
	expires_seconds=os.environ['CACHE_SECONDS'],
	threaded=os.environ['THREADED'])

@app.route('/')
@app.route(os.environ['WEB_ROOT'] + '/')
def index():
	try:
		data = mta.get_data()
		return _make_envelope(data)
	except KeyError as e:
		abort(404)

def _envelope_reduce(a, b):
	if a['last_update'] and b['last_update']:
		return a if a['last_update'] < b['last_update'] else b
	elif a['last_update']:
		return a
	else:
		return b

def _make_envelope(data):
	time = None
	if data:
		time = reduce(_envelope_reduce, data)['last_update']

	return jsonify({
		'data': data,
		'updated': time
		})

# if __name__ == '__main__':
	# app.run(host='0.0.0.0', port=8088, use_reloader=False)

