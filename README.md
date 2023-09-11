# WSGI: Web Server Gateway Interface


## Steps to set-up mod_wsgi with apache on Fedora 37:  ## 
*Note: If you're attempting to use this Framework on Unbuntu, you will need to use a different package manager like apt.*    
0. Update the OS
```sudo dnf update```

1. Install Apache using the following commands  
``` sudo dnf install httpd -y ```  
``` sudo systemctl start httpd.service ```  
– you can check the status of Apache with:     
``` sudo systemctl status httpd.service ```  

2. Install pip or another package manager. *Note: this guide will be using pip.*  
```sudo dnf install python3-pip```  

3. Run:  
```sudo dnf install httpd python-setuptools mod_wsgi```    
*This allow apache to recognize mod_wsgi as a CGI*  

4. Install mod_wsgi:  
``` pip install mod-wsgi ```  
*Note: this is likely already installed but it is good to check with this command*
– More info can be found at: https://pypi.org/project/mod-wsgi/    

5. Navigate to /etc/httpd/conf and run:  
```sudo nano httpd.conf```  
*Note: This is the main config file for Apache; its location may change*


6. Paste the following into the httpd.conf file:  

```
WSGIDaemonProcess myapp python-home=/usr/local/www/wsgi-scripts/venv/
WSGIProcessGroup myapp
WSGIApplicationGroup %{GLOBAL}
WSGIScriptAlias /app  /usr/local/www/wsgi-scripts/app.py
<Directory /usr/local/www/wsgi-scripts>
<IfVersion < 2.4>
	Order allow, deny
	Allow from all
</IfVersion>
<IfVersion >= 2.4>
	Require all granted
</IfVersion>
</Directory>
```  

Write out the changes and exit (Ctrl + O) Enter (Ctrl+X)  
For more information about configuration, check the [mod-wsgi documentation](https://modwsgi.readthedocs.io/en/master/user-guides/quick-configuration-guide.html)  

7.  In your IDE of choice, create the following file (or copy the app.py file in the repo):    

Your script should look **EXACTLY** like this.   

```py
from parse import parse
from webob import Request, Response


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


@application.route("/app")
def home(request, response):
    response.text = "Hello from the APP page"


@application.route("/app/home")
def home(request, response):
    response.text = "Hello from the HOME page"


@application.route("/app/about")
def about(request, response):
    response.text = "Hello from the ABOUT page"


@application.route("/app/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}"
```  
[^1]  
*Note: The directory location needs to match the WSGIScriptAlias location.*
It is **Highly** reccommended that you create a virtual environment for your projects. For more information about virtual environments, [read the official documentation](https://docs.python.org/3/library/venv.html)  

9. From the directory where your project lives, run the following command:
```sudo cp *.* /usr/local/www/wsgi-scripts``` 
*Note: you may need to make some of these directories with the ```sudo mkdir [folderName]```

10. Restart the server with the command:  
```sudo systemctl restart httpd.service```  

11. Open a browser on your local machine and navigate to http://localhost/app and you should see the text 'Hello from the APP page.' in your browser. 
12. Open a browser on your host machine and navigate to your Linux machine's IP ```yo.ur.ip.here/app``` to see the same message as before. 
*Note: you can find your machine's ip by running ```sudo ifconfig``` in a terminal.*  

---
## Debugging: ##  
- Inside the httpd.conf file Apache sets the loglevel to warn by default. When developing applications, it is encouraged to change the level to 'info' by changing ```LogLevel warn``` to ```LogLevel info```  

- According to the [mod-wsgi doucmentation](https://modwsgi.readthedocs.io/en/master/user-guides/quick-configuration-guide.html)  
>Messages that are logged by a WSGI application via the ‘wsgi.errors’ object passed through to the application in the WSGI environment are also logged. These will go to the virtual host error log file if it exists, or the main error log file if the virtual host is not setup with its own error log file. Thus, if you want to add debugging messages to your WSGI application code, you can use ‘wsgi.errors’ in conjunction with the ‘print’ statement as shown below:  

- Additionally, the documentation provides a sample class to track responses and requests:  
```py
import pprint

class LoggingMiddleware:

    def __init__(self, application):
        self.__application = application

    def __call__(self, environ, start_response):
        errors = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errors)

        def _start_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errors)
            return start_response(status, headers, *args)

        return self.__application(environ, _start_response)

application = LoggingMiddleware(application)
```  
- You can view the log file in a stream by opening a terminal and running the command:  
``` sudo tail -f /var/log/httpd/error_log```  
*Note: this is the default location for the Apache error log; If you are using a custom error log file, change the command accordingly.*  

- If you are experiencing issues connecting to MySQL, try the following: [Source](https://stackoverflow.com/a/56710474)
>Some things to check, assuming this is a Linux machine:
>Make sure you can connect locally using the same user name and password. mysql -u [youruser] -p
>If SELinux is running, make sure the "httpd_can_network_connect_db" boolean is set to on. 
>Check with:   
    ```sudo getsebool httpd_can_network_connect_db```    
>If it comes back as "off," set it to "on" with:    
    ```sudo setsebool -P httpd_can_network_connect_db on```  
>(Make sure to include the -P, or it will revert back to the original value if the system restarts.)



---
## Known Issues / To Do list: ##

- [ ] Fix ModuleNotFoundError experienced when import custom module.  
- [ ] Begin Integrating MySQL into application.  
- [ ] Iterate and Update Documentation as needed.   

---
## Sources / Additional Information: ##
- [TestDriven.io : WSGI framework](https://testdriven.io/courses/python-web-framework/wsgi/)  
- [TestDriven.io : Request and Routing](https://testdriven.io/courses/python-web-framework/requests-routing/)  
- [PyPi : mod-wsgi overview](https://pypi.org/project/mod-wsgi/)
- [mod_wsgi: documentation](https://modwsgi.readthedocs.io/en/master/)  
- [Toptal : WSGI overview and implementation](https://www.toptal.com/python/pythons-wsgi-server-application-interface)  

---  
## Footnotes: ##  
[^1]: The reason the code is combined in this fashion is due to a ModuleNotFoundError that needs to be resolved.
