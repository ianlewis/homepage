#:coding=utf-8:

import os
import argparse


def _call_command(name, options=None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'homepage.settings'
    from django.core.management import call_command
    call_command(name, **(options or {}))


def start(args):
    from meinheld import server
    from homepage.wsgi import application
    server.listen((args.addr, args.port))
    server.run(application)


def migrate(args):
    _call_command('syncdb', {
        'migrate': True,
        'interactive': False,
    })


def main():
    parser = argparse.ArgumentParser(description='The Homepage App')

    subparsers = parser.add_subparsers(help="Sub-command help")

    start_parser = subparsers.add_parser('start', help="Run the app server.")

    start_parser.add_argument('--addr', default='0.0.0.0',
                              help="Optional IP address to bind to")
    start_parser.add_argument('--port', default=8000, type=int,
                              help="Port to bind to")

    start_parser.set_defaults(func=start)

    migrate_parser = subparsers.add_parser('migrate',
                                           help="Migrate the database.")
    migrate_parser.set_defaults(func=migrate)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
