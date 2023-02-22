# wsgi-python
Basic WSGI framework

## Steps to set-up mod_wsgi with apache on Fedora 37:  ## 
*Note: If you're attempting to use this Framework on Unbuntu, you will need to use a different package manager like apt.*  
1. Install Apache using the following commands  
``` sudo dnf install httpd -y ```  
``` sudo systemctl start httpd.service ```  
– you can check the status of Apache with:     
``` sudo systemctl status httpd.service ```  

2. Install pip or another package manager. *Note: this guide will be using pip.*  
```sudo dnf install python3-pip```  

3. Install mod_wsgi:  
``` pip install mod-wsgi ```  
– More info can be found at: https://pypi.org/project/mod-wsgi/  

4. Run: 
```sudo dnf install httpd python-setuptool mod_wsgi```  *This allow apache to recognize mod_wsgi as a CGI*  

5. Navigate to /etc/httpd/conf and run:  
```sudo nano httpd.conf```  
– This is the main config file for Apache


6. Paste the following into the httpd.conf file:  

```
WSGIScriptAlias /myapp /usr/local/www/wsgi-scripts/myapp.py
<Directory /usr/local/www/wsgi-scripts>
<IfVersion < 2.4>
Order allow,deny
Allow from all
</IfVersion>
<IfVersion >= 2.4>
Require all granted
</IfVersion>
</Directory>
```  

Write out the changes and exit (Ctrl + O) Enter (Ctrl+X)

7.  navigate to /usr/local/www/wsgi-scripts and run: sudo nano myapp.py  

Your script should look EXACTLY like this.   
*Note: You may need to add the 'b' on line 3. This turns the string into a byte array object.*  

```
def application(environ, start_response):
status = '200 OK'
output = b'Hello World!'
response_headers = [('Content-type', 'text/plain'),
('Content-Length', str(len(output)))]
start_response(status, response_headers)
return [output]
```  

8. If the myapp.py file does not exist in the www/wsgi-scripts, you can create with the command:    
```sudo nano myapp.py```  
*Note: you must be in the /usr/local/www/wsgi-scripts folder or copy the file to that directory.*

9. Restart the server with the command:  
```sudo systemctl restart httpd.service```  

10. Open a browser on your local machine and navigate to http://localhost/myapp and you should see the text 'Hello World!' in your browser.  
