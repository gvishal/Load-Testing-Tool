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
import gevent

from flask.ext.socketio import SocketIO, emit, join_room, leave_room


from gevent import monkey
monkey.patch_all(thread=False)

app = Flask(__name__)
api = restful.Api(app)

socketio = SocketIO(app)

app.config['STATIC_FOLDER'] = 'static'
cors = CORS(app) # Cross Origin Request Implementation

dic = {}
lock = 0
job_id = 0
all_jobs = {}
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
        r = request.get_json(force=True)
        try:
            global dic
            z = request.remote_addr + ":" + r['port']
            t = {}
            t['ip'] = z
            t['port'] = r['port']
            y = time.time() - start
            t['created'] = time.time() 
            t['updated'] = time.time() 
            t['status'] = 0
            t['killed'] = -1
            t['job-given'] = 0
            t['job-received'] = 0
            t['job-completed'] = 0
            t['result'] = {}
            t['report'] = {}
            dic[z] = t
        except:
            print 'Invalid Data'
        for i in dic:
            print i
        return {'msg' : 'Connected successfully by post method'}

""" The return value of this class's method get is an HTML page which is stringyfied. 
    The function returns this value to 'get.html'.Proceed to 'get.html' to see what is done with the return value.
"""
class Slave(restful.Resource): 
    """This class is a route to check the status of the slave """
    def get(self):
        global dic           
        return dic

class Status(restful.Resource):
    def get(self):
        return getCurrentStatus()


class CurrentTimeStampData(restful.Resource):
    def get(self):
        rawReport = getCurrentStatus()
        if rawReport['status']:
            return  rawReport['time_stamp']
        return {}
       
def getCurrentStatus():
    report = {}
    all_timestamps = {}
    total_time = 0
    jobKey = None
    total_requests = 0
    global dic
    for i in dic:
        url = 'http://' + i + '/Stats'
        try:
            r = requests.get(url)
        except Exception as ext:
            print ext
            continue

        job_data = json.loads(r.text)
        print 'We got the data', job_data
        if not job_data['job_status']:
            continue

        try:
            #print 'We are here in try'
            status = job_data['summary']
            time_series = job_data['time_series']
            time_stamp = job_data['time_stamp']
            job_status = job_data['job_status']
            jobKey = job_data['jobKey']
        except:
            continue
        
        if len(status) < 2:
            continue

        total_requests += int(status['num_requests'])
        total_time += int(status['avg_response_time']) * int(status['num_requests'])
        report['name'] = status['name']
        report['method'] = status['method']
        report['num_requests'] = report.setdefault('num_requests', 0) +  int(status['num_requests'])
        report['num_failures'] = report.setdefault('num_failures', 0) + int(status['num_failures'])
        report['median_response_time'] = int(status['median_response_time'])
        report['min_response_time'] = min(report.setdefault('min_response_time', 100000), int(status['min_response_time']))
        report['max_response_time'] = max(report.setdefault('max_response_time', 0), int(status['max_response_time']))
        report['content_length'] = int(status['content_length'])
        report['num_reqs_per_sec'] = report.setdefault('num_reqs_per_sec', 0) + int(status['num_reqs_per_sec'])

        for t in time_stamp:
            all_timestamps[t] = all_timestamps.setdefault(t, {'requests': 0, 'failures': 0, 'response_time': 0, 'min_response_time': 100000, 'max_response_time': 0, 'size': 0})
            
            all_timestamps[t]['requests'] += time_stamp[t]['requests']                 
            all_timestamps[t]['failures'] += time_stamp[t]['failures']
            all_timestamps[t]['size'] = time_stamp[t]['size']
            all_timestamps[t]['response_time'] += time_stamp[t]['response_time']
            all_timestamps[t]['min_response_time'] = min(time_stamp[t]['min_response_time'], all_timestamps[t]['min_response_time'])
            all_timestamps[t]['max_response_time'] = max(time_stamp[t]['max_response_time'], all_timestamps[t]['max_response_time'])

    if len(report):
        try:
            report['avg_response_time'] = total_time / total_requests
        except:
            report['avg_response_time'] = 0

        for t in all_timestamps:
            try:
                all_timestamps[t]['avg_response_time'] = all_timestamps[t]['response_time'] / all_timestamps[t]['requests']
            except:
                all_timestamps[t]['avg_response_time'] = 0

    final_report={}
    if jobKey and status and time_stamp:
        final_report['status'] = True
        final_report['jobKey'] = jobKey
        final_report['summary'] = report
        final_report['time_stamp'] = all_timestamps
    else:
        final_report['status'] = False

    return final_report

def combine_data(job_data, jobKey):
    report = {}
    all_timestamps = {}
    total_time = 0
    total_requests = 0
    if jobKey not in all_jobs.keys():
        all_jobs[jobKey] = {}
        all_jobs[jobKey]['summary'] = {}
        all_jobs[jobKey]['time_stamp'] = {}

    status = job_data['summary']
    time_series = job_data['time_series']
    time_stamp = job_data['time_stamp']
    job_status = job_data['job_status']
    jobKey = job_data['jobKey']

    all_jobs[jobKey]['summary']['total_time'] = all_jobs[jobKey]['summary'].setdefault('total_time', 0) + int(status['avg_response_time']) * int(status['num_requests'])
    all_jobs[jobKey]['summary']['name'] = status['name']
    all_jobs[jobKey]['summary']['method'] = status['method']
    all_jobs[jobKey]['summary']['num_requests'] = all_jobs[jobKey]['summary'].setdefault('num_requests', 0) +  int(status['num_requests'])
    all_jobs[jobKey]['summary']['num_failures'] = all_jobs[jobKey]['summary'].setdefault('num_failures', 0) + int(status['num_failures'])
    all_jobs[jobKey]['summary']['median_response_time'] = int(status['median_response_time'])
    all_jobs[jobKey]['summary']['min_response_time'] = min(all_jobs[jobKey]['summary'].setdefault('min_response_time', 100000), int(status['min_response_time']))
    all_jobs[jobKey]['summary']['max_response_time'] = max(all_jobs[jobKey]['summary'].setdefault('max_response_time', 0), int(status['max_response_time']))
    all_jobs[jobKey]['summary']['content_length'] = int(status['content_length'])
    all_jobs[jobKey]['summary']['num_reqs_per_sec'] = all_jobs[jobKey]['summary'].setdefault('num_reqs_per_sec', 0) + int(status['num_reqs_per_sec'])

    for t in time_stamp:
        all_jobs[jobKey]['time_stamp'][t] = all_jobs[jobKey]['time_stamp'].setdefault(t, {'requests': 0, 'failures': 0, 'response_time': 0, 'min_response_time': 100000, 'max_response_time': 0, 'size': 0})
        
        all_jobs[jobKey]['time_stamp'][t]['requests'] += time_stamp[t]['requests']                 
        all_jobs[jobKey]['time_stamp'][t]['failures'] += time_stamp[t]['failures']
        all_jobs[jobKey]['time_stamp'][t]['size'] = time_stamp[t]['size']
        all_jobs[jobKey]['time_stamp'][t]['response_time'] += time_stamp[t]['response_time']
        all_jobs[jobKey]['time_stamp'][t]['min_response_time'] = min(time_stamp[t]['min_response_time'], all_jobs[jobKey]['time_stamp'][t]['min_response_time'])
        all_jobs[jobKey]['time_stamp'][t]['max_response_time'] = max(time_stamp[t]['max_response_time'], all_jobs[jobKey]['time_stamp'][t]['max_response_time'])

    try:
        all_jobs[jobKey]['summary']['avg_response_time'] = all_jobs[jobKey]['summary']['total_time'] / all_jobs[jobKey]['summary']['num_requests']
        round(all_jobs[jobKey]['summary']['avg_response_time'], 3)
    except:
        all_jobs[jobKey]['summary']['avg_response_time'] = 0

    for t in all_jobs[jobKey]['time_stamp']:
        try:
            all_jobs[jobKey]['time_stamp'][t]['avg_response_time'] = all_jobs[jobKey]['time_stamp'][t]['response_time'] / all_jobs[jobKey]['time_stamp'][t]['requests']
            round(all_jobs[jobKey]['time_stamp'][t]['avg_response_time'], 3)
        except:
            all_jobs[jobKey]['time_stamp'][t]['avg_response_time'] = 0

    all_jobs[jobKey]['summary']['jobKey'] = jobKey

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
        print 'We got result', jsonData
        i = request.remote_addr[:]
        i = i + ":" +jsonData['port']

        global dic

        combine_data(jsonData, jsonData['jobKey'])

        dic[i]['result'][jsonData['jobKey']] = jsonData
        dic[i]['lastjob'] = {"jobKey": jsonData['jobKey'], "summary" : jsonData["summary"]}
        y = time.time() - start
        dic[i]['job-completed'] = y
        dic[i]['status'] = 0

        return {'msg' : 'POST Message Received'}

""" The below class's method 'post' is activated when the "Start Job" button is clicked upon. 
    The job received as JSON string from post.html is sent to another server acting as a slave to this server.
"""
def worker(i,jsonData):
    ip = 'http://' + i + '/Job'
    z = time.time() - start
    dic[i]['job-given'] = z
    dic[i]['status'] = 1
    y = json.dumps(jsonData)
    r = requests.post(ip, data=y)
    return

class Job(restful.Resource):
    """Implementing api '/job'"""
    def get(self):
        """GET method in REST"""
        return {'msg' : 'I ll return job information'}

    def post(self):
        """POST method in REST"""
        if not dic:
            return {"status" : False, "msg" : "no slave found"}
        jsonData = request.get_json(force=True)
        print 'jsonData', jsonData
        jsonData['users'] = int(jsonData['users'])/len(dic)
        
        try:
            jsonData['num_tasks'] = int(jsonData['num_tasks'])/len(dic)
        except:
            jsonData['num_tasks'] = jsonData['users']*10
        #print 'dic', dic
        jsonData['jobKey'] = str(uuid.uuid1())
        x = []
        done = 1        
        for i in dic:
            if dic[i]['status'] == 0 and dic[i]['killed'] == -1:
                dic[i]['status'] = 1
                x.append(gevent.spawn(worker,i,jsonData))
                done = 0
            else:
                done = 1
        if done == 1:
            return {"status": False, 'msg' : 'All slaves are busy'}
        gevent.joinall(x)
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
                 dic[i]['updated'] = updated
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
        return all_jobs
 
    def post(self):
        return "hello"

@app.route('/')
def landing():
    return render_template('index.html')

# @app.route('/graph')
# def graph():
#     return render_template('graph.html')

@socketio.on('realTimeData')
def test_message(message):
    global dic
    global all_jobs
    while True:

        data = getCurrentStatus()
        if data['status']:
            emit('status', data)
        else:
            print 'no data found'
        # slave report 
        emit("slave", dic)
        emit("history", all_jobs)
        gevent.sleep(1.5)

api.add_resource(Connect, '/connect')
api.add_resource(Job, '/job')
api.add_resource(HealthCheck, '/healthcheck')
api.add_resource(JobResult,'/jobresult')
api.add_resource(Slave,'/slave')
api.add_resource(Status,'/status')
api.add_resource(Past,'/past')

# for graph only 
api.add_resource(CurrentTimeStampData, '/current_time_series')
start = time.time()


if __name__ == '__main__':
   # app.run(host='0.0.0.0',port=1234,debug=True,threaded=True)
   socketio.run(app, host='0.0.0.0', port=8080)
