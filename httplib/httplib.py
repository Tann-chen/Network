import socket
import sys
from urllib.parse import urlparse

def get(url,headers):

    url_parse = urlparse(url)
    host_name = url_parse.netloc.strip()
    parameters = url_parse.query.strip()
    path = url_parse.path.strip()

    # request_line
    request_message = "GET"+" "+path
    if len(parameters) > 0:
        request_message += "?"+parameters

    request_message += " "+"HTTP/1.0"+"\n"

    # header_lines
    request_message += "Host: "+host_name+"\n"
    request_message += "Connection: close\n"

    for key,value in headers.items():
        request_message += key+":"+" "+value+"\n"

    print(request_message)

    # send
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((host_name,80))
        while True:
            request = request_message.encode("utf-8")
            conn.sendall(request)
            # MSG_WAITALL waits for full request or error
            response = conn.recv(2048, socket.MSG_WAITALL)
            sys.stdout.write(response.decode("utf-8"))
    finally:
        conn.close()




def post(url,paras,headers):

    url_parse = urlparse(url)
    host_name = url_parse.netloc.strip()
    parameters = url_parse.query.strip()
    path = url_parse.path.strip()

    # request_line
    request_message = "POST" + " " + path + " " + "HTTP/1.0" + "\n"

    # header_line
    request_message += "Host: "+host_name
    request_message += "Connection: close"
    for key,value in headers.items():
        request_message += key+":"+" "+value+"\n"

    # entity_body
    for key,value in paras.items():
        request_message +=key+"="+value+"&"
    request_message = request_message.rstrip("&")

    # send
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((host_name, 80))
        while True:
            request = request_message.encode("utf-8")
            conn.sendall(request)
            # MSG_WAITALL waits for full request or error
            response = conn.recv(2048, socket.MSG_WAITALL)
            sys.stdout.write(response.decode("utf-8"))
    finally:
        conn.close()






    





