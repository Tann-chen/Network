import cmd
from server import runserver


class Httpfs(cmd.Cmd):
    prompt = ''

    def do_httpfs(self, arg):
        args = arg.split(' ')
        is_v = False
        port = 8080
        dir_path = 'server_f'

        if '-v' in args:
            is_v = True

        if '-p' in args:
            p_index = args.index('-p')
            port = args[p_index + 1]

        if '-d' in args:
            d_index = args.index('-d')
            dir_path = args[d_index + 1]

        runserver(port, is_v, dir_path)

    def do_exit(self, arg):
        return True


if __name__ == '__main__':
    Httpfs().cmdloop()
