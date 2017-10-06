import cmd
import sys
from httplib.httplib import get
from httplib.httplib import post

class Httpc (cmd.Cmd):
    prompt = 'httpc '

    def do_help(self, arg):
        if arg == 'get':
            print('usage: httpc get [-v] [-h key:value] URL')
            print('-v \t Prints the detail of the response such as protocol, status,and headers.')
            print('-h key:value  \t Associates headers to HTTP Request with the format key:value.')

        elif arg == 'post':
            print('usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL')
            print('Post executes a HTTP POST request for a given URL with inline data or from file.')
            print('-v \t Prints the detail of the response such as protocol, status,and headers.')
            print("-h key:value \t Associates headers to HTTP Request with the format'key:value'.")
            print('-d string \t Associates an inline data to the body HTTP POST request.')
            print('-f file \t Associates the content of a file to the body HTTP POST request.')
            print('Either [-d] or [-f] can be used but not both.')

        else:
            print('httpc is a curl-like application but supports HTTP protocol only.')
            print('Usage:')
            print('\t httpc command [arguments]')
            print('The commands are:')
            print('get \t executes a HTTP GET request and prints the response.')
            print('post \t executes a HTTP POST request and prints the response.')
            print('help \t prints this screen.')
            print('Use "httpc help [command]" for more information about a command.')



    def do_get(self,arg):
        args = arg.split(' ')
        is_v = False
        o_path = ''
        headers = {}
        url = args[-1]

        if '-v' in args:
            is_v = True

        if '-o' in args:
            o_index = args.index('-o')
            o_path = args[o_index+1]

        if '-h' in args:
            h_index = 0
            for i in args:
                if i == '-h':
                    header = args[h_index+1].split(':')
                    headers[header[0]] = header[1]
                h_index+=1

        get(url,headers,is_v,o_path)


    def do_post(self,arg):
        args = arg.split(' ')
        is_v = False
        o_path = ''
        headers = {}
        url = args[-1]
        data=''
        file_path=''

        if '-d' and '-f' in args:
            sys.stdout.write('illegal')
        else:
            if '-v' in args:
                is_v = True

            if '-o' in args:
                o_index = args.index('-o')
                o_path = args[o_index+1]

            if '-h' in args:
                h_index = 0
                for i in args:
                    if i == '-h':
                        header = args[h_index+1].split(':')
                        headers[header[0]] = header[1]
                    h_index+=1

            if '-d' in args:
                d_index = args.index('-d')
                data = args[d_index+1]

            if '-f' in args:
                f_index = args.index('-f')
                file_path = args[f_index+1]

            post(url,headers,is_v,data,file_path,o_path)



    def do_exit(self,arg):
    	return True


if __name__ == '__main__':
    Httpc().cmdloop()
