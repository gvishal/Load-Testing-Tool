from flask import Flask
from flask.ext import restful
from flask import jsonify
from flask import request
import requests
import json
import time

app = Flask(__name__)
api = restful.Api(app)
dic = {}
lock = 0;
work = 0

class HelloWorld(restful.Resource):
  def get(self):
    return {'msg':'HelloWorld'}

class Connect(restful.Resource):
  def get(self):
    return {'msg' : 'Connected successfully by get method'}

  def post(self):
    global work
    work = 1
    r = request.get_json(force=True)
    if r != '':
      global dic
      t = {}
      t['port'] = r['port']
      y = time.time() - start
      t['created'] = y
      t['updated'] = y
      t['status'] = 0
      t['killed'] = -1
      z = request.remote_addr + ":" + r['port']
      dic[z] = t
      print t
    work = 0
    return {'msg' : 'Connected successfully by post method'}

class Job(restful.Resource):
  
  def get(self):
   global work
   work = 1
   for i in dic:
	port = dic[i]['port']
        ip = i + ':' + port + '/Job?job=' + string
	requests.get(ip)
   work = 0
   return ({'msg' : 'I ll return job information'})
   
  def post(self):
    global work
    work = 1
    jsonData = request.get_json(force=True)
    for i in dic:
       if dic[i]['status'] == 0:
         ip = 'http://' + i + '/Job'
         print ip
         y = json.dumps(jsonData)
         r = requests.post(ip,data=y)
    work = 0
    return {'msg' : 'Job sent' }

class HealthCheck(restful.Resource):
   def get(self):
     global lock
     print lock
     if lock == 1:
        return
     while True:
      if work == 1:
	pass
      elif work == 0:
       lock = 1
       for i in dic:
         ip = 'http://'+ i + '/Health'
         print ip
         r = requests.get(ip)
         y = time.time() - start
         if r.status_code == 200:
           dic[i]['updated'] = y
         else:
           dic[i]['killed'] = y
	 print r.text
         dic[i]['status'] = r.text
         for j in dic:
           print j, dic[j]
      time.sleep(10)
      lock = 0  
     return 
   
   def post(self):
           data = request.get_json(force=True)
	   global dic
	   return

api.add_resource(HelloWorld,'/')
api.add_resource(Connect, '/connect')
api.add_resource(Job,'/job')
api.add_resource(HealthCheck,'/healthcheck')
start = time.time()
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
