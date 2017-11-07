from httplib.httplib import get
from httplib.httplib import post


class HttpObj:
    def __init__(self,obj_id):
        self.id = obj_id

    def do_get(self, arg):
        print(" ------ httpc instance [" + str(self.id) + "] sent a get request ------")
        args = arg.split(' ')
        is_v = False
        o_path = ''
        headers = {}
        url = args[-1]

        if '-v' in args:
            is_v = True

        if '-o' in args:
            o_index = args.index('-o')
            o_path = args[o_index + 1]

        if '-h' in args:
            h_index = 0
            for i in args:
                if i == '-h':
                    header = args[h_index + 1].split(':')
                    headers[header[0]] = header[1]
                h_index += 1

        get(url, headers, is_v, o_path)
        print(" ------ httpc instance [" + str(self.id) + "] finish the get request ------")

    def do_post(self, arg):
        print(" ------ httpc instance [" + str(self.id) + "] sent a post request ------")
        args = arg.split(' ')
        is_v = False
        o_path = ''
        headers = {}
        url = args[-1]
        data = ''
        file_path = ''

        if '-v' in args:
            is_v = True

        if '-o' in args:
            o_index = args.index('-o')
            o_path = args[o_index + 1]

        if '-h' in args:
            h_index = 0
            for i in args:
                if i == '-h':
                    header = args[h_index + 1].split(':')
                    headers[header[0]] = header[1]
                h_index += 1

        if '-d' in args:
            d_index = args.index('-d')
            data = args[d_index + 1]

        if '-f' in args:
            f_index = args.index('-f')
            file_path = args[f_index + 1]

        post(url, headers, is_v, data, file_path, o_path)
        print(" ------ httpc instance [" + str(self.id) + "] finish the post request ------")

