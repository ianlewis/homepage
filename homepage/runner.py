#:coding=utf-8:

import os
import argparse


def _call_command(name, options=None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'homepage.settings'
    from django.core.management import call_command
    call_command(name, **(options or {}))


def start(args):
    _call_command("run_gunicorn", {
        "bind": args.bind,
        "workers": args.workers,
        "timeout": args.timeout,
        "daemon": args.daemon,
        "pidfile": args.pidfile,
    })


def migrate(args):
    _call_command('syncdb', {
        'migrate': True,
        'interactive': False,
    })


def main():
    parser = argparse.ArgumentParser(description='The Homepage App')

    subparsers = parser.add_subparsers(help="Sub-command help")

    start_parser = subparsers.add_parser('start', help="Run the app server.")

    start_parser.add_argument('bind', nargs='?', default=None,
                              help="Optional port number, or ipaddr:port or "
                                   "unix:/path/to/sockfile")
    start_parser.add_argument('--workers', '-w', dest='workers', type=int,
                              default=None, help="The number of worker "
                              "process for handling requests.")
    start_parser.add_argument('--timeout', '-t', dest='timeout', type=int,
                              default=30, help="Workers silent for more than "
                              "this many seconds are killed and restarted.")
    start_parser.add_argument('--pid', '-d', dest='pidfile',
                              default=None,
                              help="A filename to use for the PID file.")
    start_parser.add_argument('--daemon', '-D', action='store_true',
                              dest='daemon', default=False,
                              help=" Daemonize the process..")

    start_parser.set_defaults(func=start)

    migrate_parser = subparsers.add_parser('migrate',
                                           help="Migrate the database.")
    migrate_parser.set_defaults(func=migrate)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
