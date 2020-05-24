import logging

try:
    from flask import Flask
    from flask import request
except ImportError:
    logging.fatal(
        "Failed to import Flask. Flask must be installed to run tests.")

import json

server = Flask(__name__)


def test_failed():
    return json.dumps({
        'test': 'failed'
    })


def no_record_for_card(card, token=None):
    response = {
        'msga': 'No record found for ' + card,
        'msgb': 'TEST SUCCESS',
        'err': '1'
    }
    if token is not None:
        response['token'] = token
    return json.dumps(response)


def invalid_token(token):
    return json.dumps({
        'msga': 'Invalid token ' + token,
        'msgb': 'TEST SUCCESS',
        'err': '1'
    })


@server.route('/')
def index():
    return 'Server is ready for the test!'


"""
Expected mac address 42:97:0b:27:53:86

Name    Surname     Card ID     Expected token                      Returned token
Tasha   Samson      0cb90021f6                                      thXtKt_2q7T77PsWD3hLJT34xCexmsaY
Sofia   Chadwick    f8a400ca45  thXtKt_2q7T77PsWD3hLJT34xCexmsaY    EG7I52PehLKrWB9SzKibyNVAwFKbZKi0
Salomon Hershey     f64dcf480d  EG7I52PehLKrWB9SzKibyNVAwFKbZKi0    EG7I52PehLKrWB9SzKibyNVAwFKbZKi0
"""


@server.route('/testonline', methods=['POST'])
def test_online():
    mac_address = request.args.get('mac', None)
    token = request.args.get('token', None)
    init = request.args.get('init', None)
    cardid = request.args.getlist('cardid', None)

    if mac_address is None or mac_address != '42:97:0b:27:53:86':
        return test_failed()

    if cardid is None or len(cardid) == 0:
        return test_failed()

    card = cardid[-1]

    if token is None:
        if init is None or init != '1':
            return test_failed()

        if card != '0cb90021f6':
            return no_record_for_card(card)

        return json.dumps({
            'msga': 'Tasha Samson',
            'msgb': 'TEST SUCCESS',
            'token': 'thXtKt_2q7T77PsWD3hLJT34xCexmsaY',
            'state': 'online'
        })

    if token == 'thXtKt_2q7T77PsWD3hLJT34xCexmsaY':
        if init is not None:
            return test_failed()

        if card != 'f8a400ca45':
            return no_record_for_card(card, token)

        return json.dumps({
            'msga': 'Sofia Chadwick',
            'msgb': 'TEST SUCCESS',
            'token': 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0'
        })

    if token == 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0':
        if init is not None:
            return test_failed()

        if card != 'f64dcf480d':
            return no_record_for_card(card, token)

        return json.dumps({
            'msga': 'Salomon Hershey',
            'msgb': 'TEST SUCCESS',
            'token': 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0'
        })

    return invalid_token(token)


@server.route('/testoffline', methods=['POST'])
def test_offline():
    mac_address = request.args.get('mac', None)
    token = request.args.get('token', None)
    init = request.args.get('init', None)
    cardid = request.args.getlist('cardid', None)

    if mac_address is None or mac_address != '42:97:0b:27:53:86':
        return test_failed()

    if cardid is None or len(cardid) == 0:
        return test_failed()

    card = cardid[-1]

    if token is None:
        if init is None or init != '1':
            return test_failed()

        if card != '0cb90021f6':
            return no_record_for_card(card)

        return json.dumps({
            'msga': 'Tasha Samson',
            'msgb': 'TEST SUCCESS',
            'token': 'thXtKt_2q7T77PsWD3hLJT34xCexmsaY',
            'state': 'offline'
        })

    if token == 'thXtKt_2q7T77PsWD3hLJT34xCexmsaY':
        if init is not None:
            return test_failed()

        if card != 'f8a400ca45':
            return no_record_for_card(card, token)

        return json.dumps({
            'msga': 'Sofia Chadwick',
            'msgb': 'TEST SUCCESS',
            'token': 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0'
        })

    return invalid_token(token)


if __name__ == '__main__':
    server.run()
