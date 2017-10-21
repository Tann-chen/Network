import cmd
from server.httplib.server import runserver


class Httpfs(cmd.Cmd):
    prompt = 'httpfs '

    def do_get(self, arg):
        args = arg.split(' ')
        is_v = False
        p_path = 8080
        d_path = './'

        url = args[-1]

        if '-v' in args:
            is_v = True

        if '-p' in args:
            p_index = args.index('-p')
            p_path = args[p_index+1]

        if '-d' in args:
            d_index = args.index('-d')
            d_path = args[d_index+1]

        runserver('127.0.0.1', p_path)

    def do_exit(self, arg):
        return True


if __name__ == '__main__':
    Httpfs().cmdloop()

