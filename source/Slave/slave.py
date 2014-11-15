from flask import Flask
from flask import request
from flask.ext import restful
from multiprocessing import Process
import sys
import json
import requests
import requests_store
import req_old
import time
import ast

"""Implementation of server as a part of master slave model"""
"""Author : Kavya """

app = Flask(__name__)
api = restful.Api(app)
status = 0 
#0 stands for free status,1 for in Queue status and 2 for busy status.

#shutdown ??
#status_code for every request
#check server

class HelloWorld(restful.Resource):
    def get(self):
	return {"msg" : "This is get in HelloWorld"}

class Inform(restful.Resource):
    def send_port(self):
   #     return_value = requests.get("http://localhost:" + sys.argv[3] + "/" )
   #     if return_value.status_code == requests.codes.ok:            
        try:
            requests.post("http://" + sys.argv[1] + ":" + sys.argv[2] + "/connect", data=json.dumps({'port' : sys.argv[3]}))
        except:
            # r.raise_for_status()
            # To terminate server can also use werkzeug.server.shutdown
            # server = Process(target = app.run)
            # server.terminate()
            # shutdown_server()
            # requests.get("http://localhost:1400/shutdown")
            print "hi"

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

class Job(restful.Resource):
    """ Takes the job , gets the task done and sends back the results"""
    def get(self):
        return {'msg' : 'This is get'}
    def post(self):
        get_job = request.get_json(force=True)
        job = ast.literal_eval(get_job)
        if job :            
            status = 1
            requests.get("http://" + sys.argv[1] + ":" + sys.argv[2] + "/jobresult?port=" + sys.argv[3] )
            time.sleep(5) 
            status = 2
       #     result = req_old.Start(job['url'])
            r = requests_store.Task(job['url'])
            result = r.start()
            r.print_results()
	#    print r.num_worker
        #    print result.num_tasks
        #    print result.num_requests
        #    print result.num_failures
        #    data = {"port" : sys.argv[3], "num_worker" : result.num_worker, "num_tasks" : result.num_tasks, "num_requests" : result.num_requests, "num_failures" : result.num_failures}
            data = {"port" : sys.argv[3] }
            requests.post("http://" + sys.argv[1] + ":" + sys.argv[2] + "/jobresult", data = json.dumps(data))      
            status = 0
            return
        else:
            return {'msg' : 'No job given'}

class Health(restful.Resource):
    """ Returns it's health condition""" 
    def get(self):
        return status
    def post(self):
        return 

class Stop(restful.Resource):
    def get(self):
        ins = requests_store.Task("http://localhost:1500")
        ins.stop()
        return {'msg' : 'stopped'}

Inform().send_port()

api.add_resource(HelloWorld, '/')
api.add_resource(Inform, '/Inform')
api.add_resource(Job, '/Job')
api.add_resource(Health, '/Health')
api.add_resource(Stop, '/Stop')

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=int(sys.argv[3]),threaded=True)
