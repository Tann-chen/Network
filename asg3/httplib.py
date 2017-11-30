import socket
import ipaddress
import threading
import sys
from urllib.parse import urlparse
from packet import Packet

server_port = 8080


def get(url, headers, is_v, o_path):
    url_parse = urlparse(url)
    host_name = url_parse.netloc
    host_name = 'localhost'
    parameters = url_parse.query
    path = url_parse.path

    rqst_msg = 'GET ' + path
    if len(parameters) > 0:
        rqst_msg = rqst_msg + '?' + parameters

    head_msg = ''
    if bool(headers):
        for k, v in headers.items():
            head_msg = head_msg + k + ': ' + v + '\r\n'
    rqst_msg = rqst_msg + ' HTTP/1.0\r\n' + 'Host: ' + host_name + '\r\n' + head_msg + '\r\n'

    send_message(rqst_msg, host_name, server_port)

    resp = receive()

    split_index = resp.find('\r\n\r\n') + 4
    resp_content = resp[split_index:]

    if len(o_path) > 0:
        output_2_file(o_path, resp_content)
    else:
        if not is_v:
            print('******* Response *******')
            sys.stdout.write(resp_content)
        else:
            print('******* Response *******')
            sys.stdout.write(resp)


def post(url, headers, is_v, data, file, o_path):
    url_parse = urlparse(url)
    host_name = url_parse.netloc
    host_name = 'localhost'
    parameters = url_parse.query
    path = url_parse.path

    rqst_msg = 'POST ' + path + ' HTTP/1.0\r\n'
    head_msg = ''

    if bool(headers):
        for k, v in headers.items():
            head_msg = head_msg + k + ': ' + v + '\r\n'

    entity_body = ''
    if len(parameters) > 0:
        entity_body = entity_body + parameters
    if len(data) > 0:
        entity_body = entity_body + data
    if len(file) > 0:
        with open(file) as file_obj:
            file_content = file_obj.read().rstrip()
            entity_body = entity_body + file_content

    rqst_msg = rqst_msg + 'Host: ' + host_name + '\r\nContent-Length: ' + str(
        len(entity_body)) + '\r\n' + head_msg + '\r\n'
    rqst_msg = rqst_msg + entity_body

    send_message(rqst_msg, host_name, server_port)

    resp = receive()

    split_index = resp.find('\r\n\r\n') + 4
    resp_content = resp[split_index:]

    if len(o_path) > 0:
        output_2_file(o_path, resp_content)
    else:
        if not is_v:
            print('******* Response *******')
            sys.stdout.write(resp_content)

        else:
            print('******* Response *******')
            sys.stdout.write(resp)


def output_2_file(file_path, content):
    with open(file_path, 'w') as file_obj:
        file_obj.write(content)


# ---------------------------- sending func ----------------------------

MAX_LEN = 800
sequence_number = 1  # 0 means SYN,SYN_ACK,SYN_ACK_ACK
is_handshake_success = False
window_size = 8

# sending
send_buffer = []
timeout = 5

# router
router_address = 'localhost'
router_port = 3000

# package type
P_DATA = 0
P_SYN = 1
P_SYN_ACK = 2
P_SYN_ACK_ACK = 3
P_ACK = 4
P_DATA_START = 5
P_DATA_END = 6
P_DATA_ONLY = 7


def sequence_number_plus():
    global sequence_number
    sequence_number = (sequence_number + 1) % (2 ** (4 * 8))


def send_message(msg, server_address, server_port):
    global send_buffer

    # handshake with target server
    while not is_handshake_success:
        handshake(server_address, server_port)

    # store new message to send_buffer
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_address))

    if len(msg) < MAX_LEN:
        p = Packet(packet_type=P_DATA_ONLY,
                   seq_num=sequence_number,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=msg.encode("utf-8"))
        sequence_number_plus()
        send_buffer.append(p)

    else:
        # first one pack
        first_msg = msg[:MAX_LEN - 1]
        p = Packet(packet_type=P_DATA_START,
                   seq_num=sequence_number,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
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
                       peer_port=server_port,
                       payload=payload.encode("utf-8"))
            sequence_number_plus()
            send_buffer.append(p)
            msg = msg[MAX_LEN:]

        # last one pack
        p = Packet(packet_type=P_DATA_END,
                   seq_num=sequence_number,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
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

    try:
        conn.settimeout(timeout)
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        if p.packet_type == P_ACK:
            print('receive ACK - ' + str(p.seq_num) + 'from server')
    except socket.timeout:
        print('- Timeout -')
        resend_package(pack)
    finally:
        conn.close()


def resend_package(pack):
    global timeout

    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.sendto(pack.to_bytes(), (router_address, router_port))
        print('resend NO.' + str(pack.seq_num) + 'package to server')
        conn.settimeout(timeout)
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        if p.packet_type == P_ACK:
            print('receive ACK - ' + str(p.seq_num) + 'from server')
    except socket.timeout:
        print('- Timeout -')
        resend_package(pack)
    finally:
        conn.close()


def handshake(server_address, server_port):
    global timeout
    global is_handshake_success

    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_address))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        msg = str(RECEIVE_PORT)  # tell server the receiving port of the client is 8000
        p = Packet(packet_type=P_SYN,
                   seq_num=0,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=msg.encode("utf-8"))
        conn.sendto(p.to_bytes(), (router_address, router_port))
        print('send SYN handshake to server')

        conn.settimeout(timeout)

        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)

        if p.packet_type == P_SYN_ACK:
            print('receive SYN_ACK from server')
            is_handshake_success = True

            # third handshake
            p = Packet(packet_type=P_SYN_ACK_ACK,
                       seq_num=0,
                       peer_ip_addr=peer_ip,
                       peer_port=server_port,
                       payload=''.encode("utf-8"))
            conn.sendto(p.to_bytes(), (router_address, router_port))
            print('send SYN_ACK_ACK handshake to server')

    except socket.timeout:
        print('---- Handshake fail ----')
        is_handshake_success = False

    finally:
        conn.close()


# ----------------------------  receiving func -------------------------------

RECEIVE_PORT = 8000
receive_record = []


def receive():
    content = ''
    receive_buffer = {}
    start_seq = 0
    end_seq = 0
    is_deliver = 2   # this is a flag

    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind(('localhost', RECEIVE_PORT))
        print('----- listening to response from server -----')
        while True:
            data, sender = conn.recvfrom(1024)
            p = Packet.from_bytes(data)
            ack_pack = Packet(packet_type=P_ACK,
                              seq_num=p.seq_num,
                              peer_ip_addr=p.peer_ip_addr,
                              peer_port=p.peer_port,
                              payload=''.encode("utf-8"))
            conn.sendto(ack_pack.to_bytes(), sender)

            if p.seq_num in receive_record:
                print('receive No.' + str(p.seq_num) + 'from server, repeated, drop')
            else:
                receive_record.append(p.seq_num)
                print('receive No.' + str(p.seq_num) + 'from server, load into buffer')

                if p.packet_type == P_DATA_ONLY:
                    content = p.payload.decode("utf-8")

                    break
                else:
                    receive_buffer[p.seq_num] = p

                    if p.packet_type == P_DATA_START:
                        start_seq = p.seq_num
                        is_deliver -= 1
                    if p.packet_type == P_DATA_END:
                        end_seq = p.seq_num
                        is_deliver -= 1

                    if is_deliver > 0:
                        continue

                    if check_integrate(start_seq, end_seq, receive_buffer):
                        content = ''
                        for i in range(start_seq, end_seq + 1):
                            content += receive_buffer[i].payload.decode("utf-8")

                        break

    except Exception as e:
        print("Error: ", e)
    finally:
        conn.close()

    return content


def check_integrate(start_seq, end_seq, receive_buffer):
    flag = True
    for i in range(start_seq, end_seq + 1):
        if i not in receive_buffer.keys():
            flag = False
    return flag
