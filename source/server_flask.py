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

app = Flask(__name__)
api = restful.Api(app)
app.config['STATIC_FOLDER'] = 'static'
cors = CORS(app) # Cross Origin Request Implementation
dic = {}
lock = 0

class HelloWorld(restful.Resource):
   """Implementing api '/'"""
   def get(self):
       """GET method in REST"""
       return {'msg' : 'Successfull'}

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
class Status(restful.Resource): 
    """This class is a route to check the status of the slave """
    def get(self):
        global dic                   
	d = json.dumps(dic)
	return render_template('page.html', name=d)

class Report(restful.Resource):
    def get(self):
        report = {}
        global dic
	for i in dic:
	    url = 'http://' + i + '/Stats'
	    r = requests.get(url)
            g = ast.literal_eval(r.text)
	    try:
	        f = g['status']
	    except:
                return r.text
            r = json.loads(f)
	    if r.get('msg') != None:
	        return f

            dic[i]['report'] = r
	    for j in dic[i]['report']:
                try:
	            report[j] += dic[i]['report'][j]
		except:
		    report[j] = dic[i]['report'][j]
		
        r = json.dumps(report)
	return r
#def post(self):
#	i = request.remote_addr[:]
#       global dic
#	l = request.get_json(force=True)
#	port = l['port']
#	i = i + ':' + port
#	dic[i]['report'] = l
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
	dic[i]['result'] = jsonData
	y = time.time() - start
        dic[i]['job-completed'] = y
	dic[i]['status'] = 0
	return {'msg' : 'POST Message Received'}

#The below class's method 'post' is activated when the "Start Job" button is clicked upon. The job received as JSON string from post.html is sent to another server acting as a slave to this server.
class Job(restful.Resource):
    """Implementing api '/job'"""
    def get(self):
        """GET method in REST"""
        return {'msg' : 'I ll return job information'}

    def post(self):
        """POST method in REST"""
        global work
        jsonData = request.get_json(force=True)
	jsonData['num_tasks'] = int(jsonData['num_tasks'])
	jsonData['num_tasks'] = jsonData['num_tasks']/3
	jsonData['num_workers'] = int(jsonData['num_workers'])
	jsonData['num_workers'] = jsonData['num_workers']/3
        for i in dic:
            if dic[i]['status'] == 0 and dic[i]['killed'] == -1:
                ip = 'http://' + i + '/Job'
                z = time.time() - start
	        dic[i]['job-given'] = z
		dic[i]['status'] = 1
                y = json.dumps(jsonData)
                r = requests.post(ip, data=y)
        return {'msg' : 'Job sent'}

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
	         render_template('check.html', name="Killed")
            else:
                 dic[i]['killed'] = 0
                 dic[i]['status'] = r.text
	         render_template('check.html',name=r.text)
            time.sleep(10)
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

api.add_resource(HelloWorld, '/')
api.add_resource(Connect, '/connect')
api.add_resource(Job, '/job')
api.add_resource(HealthCheck, '/healthcheck')
api.add_resource(JobResult,'/jobresult')
api.add_resource(Status,'/slave')
api.add_resource(Report,'/status')
api.add_resource(Past,'/past')
start = time.time()
if __name__ == '__main__':
   app.run(host='0.0.0.0',port=1234,debug=True,threaded=True)
