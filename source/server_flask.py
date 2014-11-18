"""Implementation of Master part of Master-Slave mode
   Author : G Pooja Shamili"""

from flask import Flask, render_template
from flask.ext import restful
from flask import jsonify
from flask import request
from flask_cors import CORS
import requests
import json
import time
import ast
import uuid
app = Flask(__name__)
api = restful.Api(app)
app.config['STATIC_FOLDER'] = 'static'
cors = CORS(app) # Cross Origin Request Implementation
dic = {}
lock = 0
job_id = 0
#dic["jobs"] = {}

class HelloWorld(restful.Resource):
   """Implementing api '/'"""
   def get(self):
       """GET method in REST"""
       return render_template('index.html')

class Connect(restful.Resource):
    """Implementing api '/connect'"""
    def get(self):
        """GET method in REST"""
        return {'msg' : 'Connected successfully by get method'}

    def post(self):
        """POST method in REST"""
        global work
        r = request.get_json(force=True)
        try:
            global dic
            t = {}
            t['port'] = r['port']
            y = time.time() - start
            t['created'] = y
            t['updated'] = y
            t['status'] = 0
            t['killed'] = -1
            t['job-given'] = 0
            t['job-received'] = 0
            t['job-completed'] = 0
            t['result'] = {}
            t['report'] = {}
            z = request.remote_addr + ":" + r['port']
            dic[z] = t
        except:
            print 'Invalid Data'
        for i in dic:
            print i
        return {'msg' : 'Connected successfully by post method'}

#The return value of this class's method get is an HTML page which is stringyfied. The function returns this value to 'get.html'.Proceed to 'get.html' to see what is done with the return value.
class Slave(restful.Resource): 
    """This class is a route to check the status of the slave """
    def get(self):
        global dic           
        return dic

class Status(restful.Resource):
    def get(self):
        report = {}
        total_time = 0
        total_requests = 0
        global dic
        for i in dic:
            url = 'http://' + i + '/Stats'
            r = requests.get(url)
            job_status = json.loads(json.loads(r.text))
            status = None
            try:
                print 'We are here in try'
                status = job_status['status']
            except:
                return json.loads(json.loads(r.text))
            
            if len(status) < 2:
                return {"status" : False, "msg" : "no stats found"}
            dic[i]['report'] = status
            print job_status

            if job_status.get('msg') != None:
                return json.loads(job_status)

            total_requests += int(dic[i]['report']['num_requests'])
            total_time += int(dic[i]['report']['avg_response_time']) * int(dic[i]['report']['num_requests'])
            report['name'] = dic[i]['report']['name']
            report['method'] = dic[i]['report']['method']
            report['num_requests'] = report.setdefault('num_requests', 0) +  int(dic[i]['report']['num_requests'])
            report['num_failures'] = report.setdefault('num_failures', 0) + int(dic[i]['report']['num_failures'])
            report['median_response_time'] = int(dic[i]['report']['median_response_time'])
            report['min_response_time'] = min(report.setdefault('min_response_time', 100000), int(dic[i]['report']['min_response_time']))
            report['max_response_time'] = max(report.setdefault('max_response_time', 0), int(dic[i]['report']['max_response_time']))
            report['content_length'] = int(dic[i]['report']['content_length'])
            report['num_reqs_per_sec'] = report.setdefault('num_reqs_per_sec', 0) + int(dic[i]['report']['num_reqs_per_sec'])
        print 'We are here'
        try:
            report['avg_response_time'] = total_time / total_requests
        except:
            report['avg_response_time'] = 0

        return report
        
        #def post(self):
        #   i = request.remote_addr[:]
        #       global dic
        #   l = request.get_json(force=True)
        #   port = l['port']
        #   i = i + ':' + port
        #   dic[i]['report'] = l
        #       return {'msg' : 'Got it!'}
        
class JobResult(restful.Resource):
    """This class id used to obtain result from the Slave"""
    def get(self):
        i = request.remote_addr[:]
        global dic
        l = request.args.get('port')
        i = i + ":" +l
        dic[i]['status'] = 2
        y = time.time() - start
        dic[i]['job-received'] = y
        return {'msg' : 'GET Message Received'}

    def post(self):
        jsonData = request.get_json(force=True)
        i = request.remote_addr[:]
        i = i + ":" +jsonData['port']
        global dic
        print jsonData
        dic[i]['result'] = jsonData
        y = time.time() - start
        dic[i]['job-completed'] = y
        dic[i]['status'] = 0
        return {'msg' : 'POST Message Received'}

""" The below class's method 'post' is activated when the "Start Job" button is clicked upon. 
    The job received as JSON string from post.html is sent to another server acting as a slave to this server.
"""

class Job(restful.Resource):
    """Implementing api '/job'"""
    def get(self):
        """GET method in REST"""
        return {'msg' : 'I ll return job information'}

    def post(self):
        """POST method in REST"""
        global work
        if not dic:
            return {"status" : False, "msg" : "no slave found"}
        jsonData = request.get_json(force=True)
        print 'jsonData', jsonData
        jsonData['users'] = int(jsonData['users'])/len(dic)
        
        try:
            jsonData['num_tasks'] = int(jsonData['num_tasks'])/len(dic)
        except:
            jsonData['num_tasks'] = jsonData['users']*10
        print 'dic', dic
        jsonData['jobKey'] = str(uuid.uuid1())
        for i in dic:
            if dic[i]['status'] == 0 and dic[i]['killed'] == -1:
                ip = 'http://' + i + '/Job'
                z = time.time() - start
                dic[i]['job-given'] = z
                dic[i]['status'] = 1

                y = json.dumps(jsonData)
                r = requests.post(ip, data=y)
        return {"status": True, 'msg' : 'Job sent'}

class HealthCheck(restful.Resource):
    """Implementing api '/health'"""
    def get(self):
        """GET method in REST"""
        global lock
        print lock
        if lock == 1:
            return
        for i in dic:
            ip = 'http://'+ i + '/Health'
            r = requests.get(ip)
            y = time.time() - start
            if r.status_code == 200:
                 dic[i]['updated'] = y
            else:
                 dic[i]['killed'] = 0
                 dic[i]['status'] = r.text
        lock = 0
        return {'msg' : 'HealthCheck done'}

    def post(self):
        """POST method in REST"""
        data = request.get_json(force=True)
        global dic
        return

class Past(restful.Resource):
    def get(self):
        return "hi"
 
    def post(self):
        return "hello"
@app.route('/')
def landing():
    return render_template('index.html')

api.add_resource(Connect, '/connect')
api.add_resource(Job, '/job')
api.add_resource(HealthCheck, '/healthcheck')
api.add_resource(JobResult,'/jobresult')
api.add_resource(Slave,'/slave')
api.add_resource(Status,'/status')
api.add_resource(Past,'/past')
start = time.time()


if __name__ == '__main__':
   app.run(host='0.0.0.0',port=1234,debug=True,threaded=True)
