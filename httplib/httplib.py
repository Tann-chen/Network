import socket
import sys
from urllib.parse import urlparse

def get(url,headers,is_v,o_path):
	url_parse = urlparse(url)
	host_name = url_parse.netloc
	parameters = url_parse.query
	path = url_parse.path

	rqst_msg = 'GET '+path
	if len(parameters)>0:
		rqst_msg = rqst_msg+'?'+parameters

	head_msg=''
	if bool(headers):
		for k,v in headers.items():
			head_msg = head_msg+k+': '+v+'\r\n'
	rqst_msg = rqst_msg+' HTTP/1.0\r\n'+'Host: '+host_name+'\r\n'+head_msg+'\r\n'

	# send
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		conn.connect((host_name,80))
		while True:
			rqst = rqst_msg.encode("utf-8")
			conn.sendall(rqst)
			# MSG_WAITALL waits for full request or error
			resp = conn.recv(1024, socket.MSG_WAITALL).decode("utf-8")
			split_index = resp.find('\r\n\r\n')+4
			resp_content = resp[split_index:]

			if len(o_path)>0:
				output_2_file(o_path,resp_content)
				break
			else:
				if not is_v:
					sys.stdout.write(resp_content)
				else:
					sys.stdout.write(resp)
	
	except IOError as e:
		print('')
	finally:
		conn.close()



def post(url,headers,is_v,data,file,o_path):
	url_parse = urlparse(url)
	host_name = url_parse.netloc
	parameters = url_parse.query
	path = url_parse.path

	rqst_msg = 'POST '+path+' HTTP/1.0\r\n'
	head_msg=''
	
	if bool(headers):
		for k,v in headers.items():
			head_msg = head_msg+k+': '+v+'\r\n'

	entity_body = ''
	if len(parameters) > 0:
		entity_body = entity_body+parameters
	if len(data) > 0:
		entity_body = entity_body+data
	if len(file) > 0:
		with open(file) as file_obj:
			file_content = file_obj.read().rstrip()
			entity_body = entity_body+file_content

	
	rqst_msg = rqst_msg+'Host: '+host_name+'\r\nContent-Length: '+str(len(entity_body))+'\r\n'+head_msg+'\r\n'
	rqst_msg = rqst_msg+entity_body

	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		conn.connect((host_name,80))
		while True:
			rqst = rqst_msg.encode("utf-8")
			conn.sendall(rqst)
			# MSG_WAITALL waits for full request or error
			resp = conn.recv(1024, socket.MSG_WAITALL).decode("utf-8")
			split_index = resp.find('\r\n\r\n')+4
			resp_content = resp[split_index:]

			if len(o_path)>0:
				output_2_file(o_path,resp_content)
				break
			else:
				if not is_v:
					sys.stdout.write(resp_content)
				else:
					sys.stdout.write(resp)

	except IOError as e:
		print('')
	finally:
		conn.close()



def output_2_file(file_path,content):
	with open(file_path,'w') as file_obj:
		file_obj.write(content)







