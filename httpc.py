import cmd
from httplib.httplib import get
from httplib.httplib import post

class Httpc (cmd.Cmd):
    prompt = 'httpc '
    file = None

    # help command
    def do_help(self, arg):
        if arg == 'get':
            print("usage: httpc get [-v] [-h key:value] URL")
            print("-v \t Prints the detail of the response such as protocol, status,and headers.")
            print("-h key:value  \t Associates headers to HTTP Request with the format key:value'.")

        elif arg == 'post':
            print("usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL")
            print("Post executes a HTTP POST request for a given URL with inline data or from file.")
            print("-v \t Prints the detail of the response such as protocol, status,and headers.")
            print("-h key:value \t Associates headers to HTTP Request with the format'key:value'.")
            print("-d string \t Associates an inline data to the body HTTP POST request.")
            print("-f file \t Associates the content of a file to the body HTTP POST request.")
            print("Either [-d] or [-f] can be used but not both.")

        else:
            print("httpc is a curl-like application but supports HTTP protocol only.")
            print("Usage:")
            print("\t httpc command [arguments]")
            print("The commands are:")
            print("get \t executes a HTTP GET request and prints the response.")
            print("post \t executes a HTTP POST request and prints the response.")
            print("help \t prints this screen.")
            print('Use "httpc help [command]" for more information about a command.')

    # get command
    def do_get(self,arg):
        args = arg.split(' ')
        is_v = False
        headers = {}
        url = args[-1]

        if '-v' in args:
            is_v = True
        if '-h' in args:
            for i in args:
                if args[i] == '-h':
                    header = args[i+1].split(':')
                    headers[header[0]] = header[1]
        get(url,headers)


if __name__ == '__main__':
    Httpc().cmdloop()

