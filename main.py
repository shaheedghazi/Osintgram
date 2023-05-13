import yaml
import sys
import signal
import argparse
import readline
from src import utils
from src import OsintgramStatus
from src import printcolors as pc
from src.Osintgram import Osintgram

def signal_handler(sig, frame):
    pc.printout("\nGoodbye!\n", pc.RED)
    sys.exit(0)

def _quit():
    pc.printout("Goodbye!\n", pc.RED)
    sys.exit(0)   

def configure_parser():
    parser = argparse.ArgumentParser(description='Osintgram is an OSINT tool on Instagram. It offers an interactive shell '
                                                 'to perform analysis on Instagram accounts of any users by their nickname')
    parser.add_argument('id', type=str, help='username')
    parser.add_argument('-C', '--cookies', help="clear's previous cookies", action="store_true")
    parser.add_argument('-j', '--json', help='save commands output as JSON file', action='store_true')
    parser.add_argument('-f', '--file', help='save output in a file', action='store_true')
    parser.add_argument('-c', '--command', help='run in single command mode & execute provided command', action='store')
    parser.add_argument('-o', '--output', help='where to store photos', action='store')
    return parser.parse_args()

def load_setup():
    with open("src/setup.yaml", 'r') as stream:
        return yaml.safe_load(stream)

def main():
    args = configure_parser()    
    signal.signal(signal.SIGINT, signal_handler)

    setup = load_setup()
    utils.printlogo(setup['version'], setup['author'])

    status = OsintgramStatus.OsintgramStatus()
    api = Osintgram(args.id, args.file, args.json, args.command, args.output, args.cookies)

    status.set_commands(setup['commands'])
    status.set_output_config(setup['output_config'])
    status.set_target(api.get_target())

    while True:
        signal.signal(signal.SIGINT, signal_handler)

        completer = utils.Completer(status.get_commands())
        readline.set_completer_delims(' \t\n;')
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

        if(status.is_command_mode()):
            pc.printout(status.get_command() + '> ', pc.GREEN)
        else:
            pc.printout("Run a command: ", pc.YELLOW)
        cmd = input()

        if cmd in status.get_commands():
            _cmd = cmd

            if status.is_command_mode():
                status.set_subcommand(cmd)
            else:
                status.set_command(cmd)
        else:
            _cmd = None

        if _cmd:
            __import__(status.get_module())
            mymodule = sys.modules[status.get_module()]
            if status.is_subcommand():
                command.__getattribute__(_cmd)()
            else:
                command = mymodule.Command(status, api)

        elif _cmd == "":
            print("")
        else:
            pc.printout("Unknown command\n", pc.RED)

        if args.command:
            break

if __name__ == '__main__':
    main()
