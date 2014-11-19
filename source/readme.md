
#Instructions

##Setup:

    'sudo pip install -r requirements.txt'

##Usage:

### Run server(default port: 8080):
    'python server_flask.py'

### Run slave:
    'python slave.py --masterUrl [server_ip] --masterPort [server_port] --slavePort [own_port]'

    eg.
    'python slave.py --masterUrl 0.0.0.0 --masterPort 8080 --slavePort 1500'

### Run Test Server(default port:8000):
    'python test_server'
