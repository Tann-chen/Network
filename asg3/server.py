import socket
import threading
import ipaddress
from fileapp import FileApp
from packet import Packet

# package type
P_DATA = 0
P_SYN = 1
P_SYN_ACK = 2
P_SYN_ACK_ACK = 3
P_ACK = 4
P_DATA_START = 5
P_DATA_END = 6
P_DATA_ONLY = 7


def check_integrate(start_seq, end_seq, receive_buffer):
    flag = True
    for i in range(start_seq, end_seq + 1):
        if i not in receive_buffer.keys():
            flag = False
    return flag


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


def runserver(port, is_v, dir_path):
    client_receive_port = 0
    is_access = False

    receive_record = []
    receive_buffer = {}
    start_seq = 0
    end_seq = 0
    is_deliver = 2  # this is a flag

    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # receiving socket

    try:
        listener.bind(('localhost', port))
        print('server listen to localhost:' + str(port))

        while True:
            data, sender = listener.recvfrom(1500)
            p = Packet.from_bytes(data)
            sender_addr = p.peer_ip_addr
            sender_port = p.peer_port
            seq = p.seq_num

            if p.packet_type == P_SYN:
                client_receive_port = int(p.payload.decode("utf-8"))
                print('Server receives SYN, client receiving port is ' + str(client_receive_port))
                is_access = True

                # send SYN_ACK
                ack_pack = Packet(packet_type=P_SYN_ACK,
                                  seq_num=0,
                                  peer_ip_addr=sender_addr,
                                  peer_port=sender_port,
                                  payload='ACK_SYN'.encode("utf-8"))
                listener.sendto(ack_pack.to_bytes(), sender)  # sender is router

            elif p.packet_type == P_SYN_ACK_ACK:
                print('Server receives SYN_ACK_ACK, finish tree-times handshake')

            elif is_access:
                # send ACK
                ack_pack = Packet(packet_type=P_ACK,
                                  seq_num=seq,
                                  peer_ip_addr=sender_addr,
                                  peer_port=sender_port,
                                  payload='ACK'.encode("utf-8"))
                listener.sendto(ack_pack.to_bytes(), sender)  # sender is router

                if seq in receive_record:
                    print('receive No.' + str(p.seq_num) + 'from server, repeated, drop')
                else:
                    receive_record.append(seq)
                    print('receive No.' + str(p.seq_num) + 'from server, load into buffer')

                    # deal with packs
                    if p.packet_type == P_DATA_ONLY:
                        reqst = p.payload.decode("utf-8")

                        # biz logic
                        threading.Thread(target=handler, args=(reqst, client_receive_port, is_v, dir_path)).start()

                        # clear buffer
                        receive_buffer.clear()
                        start_seq = 0
                        end_seq = 0

                    else:
                        # buffer pack
                        receive_buffer[seq] = p

                        if p.packet_type == P_DATA_START:
                            start_seq = seq
                            is_deliver -= 1
                        if p.packet_type == P_DATA_END:
                            end_seq = seq
                            is_deliver -= 1

                        if is_deliver > 0:
                            continue

                        if check_integrate(start_seq, end_seq, receive_buffer):
                            reqst = ''
                            for i in range(start_seq, end_seq + 1):
                                reqst += receive_buffer[i].payload.decode("utf-8")
                            # biz
                            threading.Thread(target=handler, args=(reqst, client_receive_port, is_v, dir_path)).start()

                            # clear buffer, init params
                            receive_buffer.clear()
                            start_seq = 0
                            end_seq = 0
                            is_deliver = 2

    # except Exception as e:
    #     if is_v:
    #         print(e)
    finally:
        listener.close()


def handler(request, recv_port, is_v, dir_path):
    recv_addr = 'localhost'

    if is_v:
        print('---- Server receive a new request ----')
    if is_v:
        print('raw request:\n' + request)

    # parse the request message
    reqst_index = request.find('\r\n')
    request_line = request[:reqst_index]
    if is_v:
        print('* request line:' + request_line)
    reqst_index_contents = request_line.split()
    reqst_method = reqst_index_contents[0]
    reqst_url = reqst_index_contents[1]
    if is_v:
        print('* request method:' + reqst_method)
        print('* request url:' + reqst_url)
    body_index = request.find('\r\n\r\n') + 4
    body_content = request[body_index:]
    if is_v:
        print('* body content:' + body_content)

    # default value
    status = 0
    content = ''
    content_type = ''

    # file app logic
    if reqst_method == 'GET':
        if reqst_url == '/':
            fileapp = FileApp()
            fileapp.get_all_files(dir_path)
            status = fileapp.status
            content = fileapp.content
            content_type = fileapp.content_type
        else:
            fileapp = FileApp()
            file_name = reqst_url[1:]
            fileapp.get_content(dir_path, file_name)
            status = fileapp.status
            content = fileapp.content
            content_type = fileapp.content_type

    elif reqst_method == 'POST':
        fileapp = FileApp()
        file_name = reqst_url[1:]
        fileapp.post_content(dir_path, file_name, body_content)
        if is_v:
            print('* body-content:' + body_content)
        status = fileapp.status
        content = fileapp.content
        content_type = fileapp.content_type

    # response
    resp_msg = 'HTTP/1.1 ' + str(status) + ' ' + status_phrase_maping(status) + '\r\n'
    resp_msg = resp_msg + 'Connection: close\r\n' + 'Content-Length: ' + str(len(content)) + '\r\n'
    resp_msg = resp_msg + 'Content-Type: ' + content_type + '\r\n\r\n'
    resp_msg = resp_msg + content
    if is_v:
        print('**** response msg **** \n' + resp_msg)

    # send response msg
    send_message(resp_msg, recv_addr, recv_port)

# ---------------------------- sending func ----------------------------


MAX_LEN = 800
sequence_number = 1  # 0 means SYN,SYN_ACK,SYN_ACK_ACK
window_size = 8

# sending
send_buffer = []
timeout = 5

# router
router_address = 'localhost'
router_port = 3000


def sequence_number_plus():
    global sequence_number
    sequence_number = (sequence_number + 1) % (2 ** (4 * 8))


def send_message(msg, recv_address, recv_port):
    global send_buffer

    # store new message to send_buffer
    peer_ip = ipaddress.ip_address(socket.gethostbyname(recv_address))

    if len(msg) < MAX_LEN:
        p = Packet(packet_type=P_DATA_ONLY,
                   seq_num=sequence_number,
                   peer_ip_addr=peer_ip,
                   peer_port=recv_port,
                   payload=msg.encode("utf-8"))
        sequence_number_plus()
        send_buffer.append(p)

    else:
        # first one pack
        first_msg = msg[:MAX_LEN - 1]
        p = Packet(packet_type=P_DATA_START,
                   seq_num=sequence_number,
                   peer_ip_addr=peer_ip,
                   peer_port=recv_port,
                   payload=first_msg.encode("utf-8"))
        sequence_number_plus()
        send_buffer.append(p)

        msg = msg[MAX_LEN:]

        # middle pack
        while len(msg) > MAX_LEN:
            payload = msg[:MAX_LEN - 1]
            p = Packet(packet_type=P_DATA,
                       seq_num=sequence_number,
                       peer_ip_addr=peer_ip,
                       peer_port=recv_port,
                       payload=payload.encode("utf-8"))
            sequence_number_plus()
            send_buffer.append(p)

            msg = msg[MAX_LEN:]

        # last one pack
        p = Packet(packet_type=P_DATA_END,
                   seq_num=sequence_number,
                   peer_ip_addr=peer_ip,
                   peer_port=recv_port,
                   payload=msg.encode("utf-8"))
        sequence_number_plus()
        send_buffer.append(p)

    # send packs in buffer
    if window_size > len(send_buffer):
        window_packages = []

        for p in send_buffer:
            window_packages.append(p)
        send_window_packs(window_packages)

    else:
        while len(send_buffer) > window_size:
            window_packages = []
            for i in range(0, window_size):
                window_packages.append(send_buffer[i])
            send_window_packs(window_packages)

            send_buffer = send_buffer[window_size:]

        # left len < window size
        window_packages = []

        for p in send_buffer:
            window_packages.append(p)
        send_window_packs(window_packages)

    # clear buffer
    send_buffer.clear()


def send_window_packs(window_packs):
    thread_pool = []

    for pack in window_packs:
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            conn.sendto(pack.to_bytes(), (router_address, router_port))
            print('send NO.' + str(pack.seq_num) + 'package to server')
            t = threading.Thread(target=listen_conn_threading, args=(conn, pack))
            t.start()
            thread_pool.append(t)

        except Exception as e:
            print("Error: ", e)

    # joins the thread
    for t in thread_pool:
        t.join()


def listen_conn_threading(conn, pack):
    global timeout

    conn.settimeout(timeout)
    try:
        response, sender = conn.recvfrom(1500)
        p = Packet.from_bytes(response)
        if p.packet_type == P_ACK:
            print('receive ACK - ' + str(p.seq_num) + 'from client')
    except socket.timeout:
        print('--- Timeout ---')
        resend_package(pack)
    finally:
        conn.close()


def resend_package(pack):
    global timeout

    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.sendto(pack.to_bytes(), (router_address, router_port))
        print('resend NO.' + str(pack.seq_num) + 'package to client')
        conn.settimeout(timeout)
        response, sender = conn.recvfrom(1500)
        p = Packet.from_bytes(response)
        if p.packet_type == P_ACK:
            print('receive ACK - ' + str(p.seq_num) + 'from client')
    except socket.timeout:
        print('--- Timeout ---')
        resend_package(pack)
    finally:
        conn.close()
