from gevent import pywsgi

content = '''
<!DOCTYPE html>
<html ng-app="robo">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>robustest-perftesting</title>
    <!-- Bootstrap Core CSS -->
    <link href="static/css/bootstrap.min.css" rel="stylesheet">
    <link href="static/css/main.css" rel="stylesheet">
</head>

 <script src='static/js/d3.v3.min.js'></script>

  <script>
    if (document.location.search.match(/type=embed/gi)) {
      window.parent.postMessage('resize', "*");
    }
  </script>
<body>

    <div id="wrapper">

        <!-- Navigation -->
        <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
            <!-- Brand and toggle get grouped for better mobile display -->
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="index.html">Performance Testing</a>
            </div>
            <!-- Top Menu Items -->
            
            <div class="collapse navbar-collapse navbar-ex1-collapse">
                <ul class="nav navbar-nav side-nav">
                    <li class="active">
                        <a href="#/newtask"><i class="fa fa-fw fa-dashboard"></i> New Task</a>
                    </li>
                    <li>
                        <a href="#/slave"><i class="fa fa-fw fa-bar-chart-o"></i> Slave</a>
                    </li>
                    <li>
                        <a href="#/report"><i class="fa fa-fw fa-table"></i> Reports</a>
                    </li>
                    <li>
                        <a href="#/history"><i class="fa fa-fw fa-table"></i> Job History</a>
                    </li>
                </ul>
            </div>
            <!-- /.navbar-collapse -->
        </nav>

        <div id="page-wrapper">
            <div class="container-fluid">

                <div ng-view></div>

            </div>
        </div>
    </div>
    <script src="static/js/jquery.js"></script>
    <script src="static/js/bootstrap.min.js"></script>
    <script src="static/js/angular.min.js"></script>
    <script src="static/js/angular-route.js"></script>
    <script src="static/js/socket.io.js"></script>
    <script src="static/js/socket.min.js"></script>
    <script src="static/js/app.js"></script>
</body>

</html>
'''

def hello_world(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html'),("Access-Control-Allow-Origin", "*")])
    yield '<b>Hello world!</b>\n'

def hello_world2(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html'),("Access-Control-Allow-Origin", "*")])
    yield '<b>%s</b>\n' % content

server = pywsgi.WSGIServer(
    ('', 8000), hello_world2)

server.serve_forever()
