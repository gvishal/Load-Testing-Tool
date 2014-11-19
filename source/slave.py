from flask import Flask
from flask import request
from flask.ext import restful
import sys
import json
import requests
import requests_store
import time
import argparse

"""Implementation of server as a part of master slave model"""
"""Author : Kavya """

app = Flask(__name__)
api = restful.Api(app)
status = 0 
#0 stands for free status,1 for in Queue status and 2 for busy status

instance = None
jobKey = None

class Parse():
    def parse(self):
        parser = argparse.ArgumentParser(description='Parsing command line arguments')
        parser.add_argument('--masterUrl', action="store", dest="masterUrl")
        parser.add_argument('--masterPort', action="store", dest="masterPort")
        parser.add_argument('--slavePort', action="store", dest="slavePort")
        args =  parser.parse_args()
        return parser.parse_args()

#class Inform(restful.Resource):
#    def send_port(self):
#        requests.post("http://" + sys.argv[1] + ":" + sys.argv[2] + "/connect", data=json.dumps({'port' : sys.argv[3]}))

class Job(restful.Resource):
    """ Takes the job , gets the task done and sends back the results"""
    def post(self):
        global instance
        global jobKey
        job = request.get_json(force = True)
        if job :
            print 'Got new job' , job            
            status = 1
            requests.get("http://" + args.masterUrl + ":" + args.masterPort + "/jobresult?port=" + args.slavePort )
             
            status = 2
            url = job["url"] or "http://localhost:8080"
            num_workers = int(job["users"]) or 100
            num_tasks = int(job["num_tasks"]) or num_workers * 100
            jobKey = job['jobKey']
            instance = requests_store.Task(url, num_workers , num_tasks, jobKey)
            result = instance.start(args.masterUrl , args.masterPort, args.slavePort , jobKey )
            print 'completed job', result
            # requests.post("http://" + sys.argv[1] + ":" + sys.argv[2] + "/jobresult", data = json.dumps(final_report))      
            status = 0
            return 
        else:
            return {'Msg' : 'No job given'}

class Stats(restful.Resource):
    def get(self):
        global jobKey
        global instance
        report = {}
        status_dic = {}
        if not instance:
            return {"status":{"msg" : "No job running" },"job_status":False}
        try:
            report["job_status"] = instance.status
            report["jobKey"] = jobKey
            report["summary"] = json.loads(instance.json_output_status(jobKey))
            report["time_series"] = json.loads(instance.json_output_timeseries(jobKey))
            report["time_stamp"] = json.loads(instance.json_output_timestamp(jobKey))
            print "Stats:Get::Successful in returning stats"
        except:
            e = sys.exc_info()[0]
            report["status"] = {"msg" : "Error occurred: " + str(e) }
            report["job_status"] = False

        return report

class Health(restful.Resource):
    """ Returns it's health condition""" 
    def get(self):
        return status

class Stop(restful.Resource):
    def get(self):
        try:
            instance.stop()
            return {'msg' : 'stopped'}
        except:
            return {'msg' : 'No job started'}

@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#Inform().send_port()

#api.add_resource(Inform, '/Inform')
api.add_resource(Job, '/Job')
api.add_resource(Health, '/Health')
api.add_resource(Stats, '/Stats')
api.add_resource(Stop, '/Stop')

if __name__ == '__main__':
    try:
        args = Parse().parse()
        print args.masterUrl, args.masterPort, args.slavePort
        requests.post("http://" + args.masterUrl + ":" + args.masterPort + "/connect", data=json.dumps({'port' : args.slavePort }))
        app.run( host='0.0.0.0', port=int(args.slavePort), threaded=True)
    except:
        print "Master not yet started"
        