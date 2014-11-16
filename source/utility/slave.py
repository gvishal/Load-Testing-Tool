from flask import Flask 
from flask import request
from flask.ext import restful
from multiprocessing import Process
import sys
import json
import requests
import requests_store
import time

app = Flask(__name__)
api = restful.Api(app)
status = 0 #0 stands for free status while 1 stands for busy status.

#status_code for every request

class HelloWorld(restful.Resource):
    def get(self):
	return { 'msg' : "This is get in HelloWorld"}

class Inform(restful.Resource):
    def sends(self):
        r = requests.post("http://" + sys.argv[1] + ":" + sys.argv[2] + "/connect", data = json.dumps({'port' : sys.argv[3]}))
        if r.status_code == requests.codes.ok :                
            return {'msg' : r.status_code}
        else:
            # r.raise_for_status()
            # To terminate server can also use werkzeug.server.shutdown
            #server = Process(target = app.run)
            #server.terminate()
            return {'msg' : 'flop'}

class Do_Task(restful.Resource):
    def __init__(self,url):
        self.url = url
    def perform_task(self):
        time.sleep(20)
        return self.url

class Job(restful.Resource):
    def get(self):
        return {'msg' : 'This is get'}
    def post(self):
        job = request.get_json( force = True)
        if job != '' :
            status = 1
           # ins = Do_Task(job["url"])
           # result = ins.perform_task()      
           # print result
            result = requests_store.global_stats.num_requests 
            print result           
            return {'msg' : "Successful"}
        else:
            return {'msg' : 'No job given'}

class Health(restful.Resource):
    def get(self):
#        requests.post("http://" + sys.argv[1] + ":" + sys.argv[2] + "/status",data = json.dumps({'status' : status}))
#        return {'msg' : status}
         return status
    def post(self):
        return {'msg' : 'post in health'}

instance = Inform()
instance.sends()

api.add_resource(HelloWorld, '/')
api.add_resource(Inform, '/Inform')
api.add_resource(Job, '/Job')
api.add_resource(Health, '/Health')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = int(sys.argv[3]))


