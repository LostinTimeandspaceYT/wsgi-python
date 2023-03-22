from parse import parse
from webob import Request, Response
from mysql.connector import (connection)
from mysql.connector import errorcode
import threading
import pprint
import time
import os
import json

class create_dict(dict): 
  
    # __init__ function 
    def __init__(self): 
        self = dict() 
          
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value

class LoggingInstance:
    def __init__(self, start_response, oheaders, ocontent):
        self.__start_response = start_response
        self.__oheaders = oheaders
        self.__ocontent = ocontent

    def __call__(self, status, headers, *args):
        pprint.pprint((status, headers)+args, stream=self.__oheaders)
        self.__oheaders.close()

        self.__write = self.__start_response(status, headers, *args)
        return self.write

    def __iter__(self):
        return self

    def write(self, data):
        self.__ocontent.write(data)
        self.__ocontent.flush()
        return self.__write(data)

    def next(self):
        data = self.__iterable.next()
        self.__ocontent.write(data)
        self.__ocontent.flush()
        return data

    def close(self):
        if hasattr(self.__iterable, 'close'):
            self.__iterable.close()
        self.__ocontent.close()

    def link(self, iterable):
        self.__iterable = iter(iterable)

class LoggingMiddleware:

    def __init__(self, application, savedir):
        self.__application = application
        self.__savedir = savedir
        self.__lock = threading.Lock()
        self.__pid = os.getpid()
        self.__count = 0

    def __call__(self, environ, start_response):
        self.__lock.acquire()
        self.__count += 1
        count = self.__count
        self.__lock.release()

        key = "%s-%s-%s" % (time.time(), self.__pid, count)

        iheaders = os.path.join(self.__savedir, key + ".iheaders")
        iheaders_fp = open(iheaders, 'w')

        icontent = os.path.join(self.__savedir, key + ".icontent")
        icontent_fp = open(icontent, 'w+b')

        oheaders = os.path.join(self.__savedir, key + ".oheaders")
        oheaders_fp = open(oheaders, 'w')

        ocontent = os.path.join(self.__savedir, key + ".ocontent")
        ocontent_fp = open(ocontent, 'w+b')

        errors = environ['wsgi.errors']
        pprint.pprint(environ, stream=iheaders_fp)
        iheaders_fp.close()

        length = int(environ.get('CONTENT_LENGTH', '0'))
        input = environ['wsgi.input']
        while length != 0:
            data = input.read(min(4096, length))
            if data:
                icontent_fp.write(data)
                length -= len(data)
            else:
                length = 0
        icontent_fp.flush()
        icontent_fp.seek(0, os.SEEK_SET)
        environ['wsgi.input'] = icontent_fp

        iterable = LoggingInstance(start_response, oheaders_fp, ocontent_fp)
        iterable.link(self.__application(environ, iterable))
        return iterable

class API:

    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        return None, None

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        if handler is not None:
            handler(request, response, **kwargs)
        else:
            self.default_response(response)


        return response


application = API()
config = {
    'user': 'root',
    'password': 'nhti',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'movies',
    'raise_on_warnings': True
}


@application.route("/app/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}"


@application.route("/app/theaters")
def theaters(request, response):
    cnx = connection.MySQLConnection(**config)
    cursor = cnx.cursor()
    query = "SELECT * from Theater"
    cursor.execute(query)
    theaters = []
    for t in cursor:
        theaters.append({"theater_id": t[0], "name":t[1], "address":t[2], "city":t[3], "state":t[4],
                        "zip":t[5], "phone":t[6], "website":t[7]})
    
    json_str = json.dumps(theaters, indent=2, sort_keys=True, default=str)
    print(json_str.encode())
    response.text = json_str
    cnx.close()


@application.route("/app/movies")
def movies(request, response):

    cnx = connection.MySQLConnection(**config)
    cursor = cnx.cursor()
    query = "SELECT * FROM Movie"
    cursor.execute(query)
    movies = []

    for title in cursor:
        movies.append({"m_id": title[0], "m_title": title[1], "genre": title[2], "minutes": title[3],
                      "release_date": title[4], "budget": title[5], "r_id": title[6], "studio_id": title[7]})
        
    json_str = json.dumps(movies, indent=2, sort_keys=True, default=str)
    print(json_str.encode())
    response.text = json_str  
    cnx.close()


@application.route("/app/movies/{id}")
def get_movie(request, response, id):

    cnx = connection.MySQLConnection(**config)
    cursor = cnx.cursor()
    query = f"SELECT * FROM Movie WHERE m_id={id}"

    cursor.execute(query)
    movie = []
    for title in cursor:
        movie.append({"m_id": title[0], "m_title": title[1], "genre": title[2], "minutes": title[3],
                      "release_date": title[4], "budget": title[5]})
    
    json_str = json.dumps(movie, indent=2, sort_keys=True, default=str)
    print(json_str.encode())
    response.text = json_str
    cnx.close()


@application.route("/app/theatermovies/{id}")
def theater_movie(request, response, id):

    cnx = connection.MySQLConnection(**config)
    cursor = cnx.cursor()
    query = f"SELECT TheaterMovie.theater_id, Theater.name, Movie.m_title FROM TheaterMovie INNER JOIN Movie ON TheaterMovie.m_id = Movie.m_idINNER JOIN Theater ON TheaterMovie.theater_id = Theater.theater_id WHERE TheaterMovie.theater_id = {id};"
    cursor.execute(query)

    movies = []

    for movie in cursor:
        movies.append({"theater_id":movie[0],"name":movie[1], "m_title": movie[2]})
    
    json_str = json.dumps(movies, indent=2, sort_keys=True, default=str)
    response.text = json_str
    cnx.close()


