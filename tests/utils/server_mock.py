import logging

try:
    from flask import Flask
    from flask import request
except ImportError:
    logging.fatal(
        "Failed to import Flask. Flask must be installed to run tests.")

import json

server = Flask(__name__)


@server.route('/')
def index():
    return 'Server is ready for the test!'


@server.route('/testconnection', methods=['POST'])
def post_testconnection():
    if '0123456789' in request.args.getlist('cardid'):
        return json.dumps({'msg': 'Test successful'})
    return json.dumps({'msg': 'Test failed'})


@server.route('/testrecorder', methods=['POST'])
def post_testrecorder():
    pass


if __name__ == '__main__':
    server.run()
