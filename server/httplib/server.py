import socket
import datetime
import os
import threading


def runserver(host, port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(5)
        while True:
            conn, addr = listener.accept()
            threading.Thread(target=handler, args=conn).start()
    except IOError as e:
        print(e)
    finally:
        listener.close()


def handler(conn):
    try:
        while True:
            request = conn.recv(1024)

            # parse the request message
            reqst_index = request.find('\r\n')
            request_line = request[:reqst_index]
            reqst_index_contents = request_line.split()
            reqst_method = reqst_index_contents[0]
            reqst_url = reqst_index_contents[1]

            body_index = request.find('\r\n\r\n') + 4
            body_content = request[body_index:]

            # response
            # default value
            status = 200
            content = ''
            content_type = get_content_type('none')

            # response message
            gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
            resp_msg = 'HTTP/1.1 ' + str(status) + ' ' + status_phrase_maping(status) + '\r\n'
            resp_msg = resp_msg + 'Connection: close\r\n' + 'Date: ' + datetime.datetime.utcnow().strftime(gmt_format) + '\r\n'
            resp_msg = resp_msg + 'Content-Length: ' + str(len(content)) + '\r\n' + 'Content-Type: ' + content_type
            conn.sendall(resp_msg)
    except IOError as e:
        print(e)
    finally:
        conn.close()


def status_phrase_maping(status):
    phrase = ''
    if status == 200:
        phrase = 'OK'
    if status == 301:
        phrase = 'Moved Permanently'
    if status == 400:
        phrase = 'Bad Request'
    if status == 404:
        phrase = 'Not Found'
    if status == 505:
        phrase = 'HTTP Version Not Supported'
    return phrase


def get_content_type(file_name):
    content_type = 'text/plain'
    suffix = os.path.splitext(file_name)[-1]
    if suffix == '.json':
        content_type = 'application/json'
    if suffix == '.html':
        content_type = 'text/html'
    if suffix == '.xml':
        content_type = 'text/xml'
    return content_type
