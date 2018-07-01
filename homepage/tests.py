import os
import sys

def main():
    sys.exc_clear()

    os.environ['DJANGO_SETTINGS_MODULE'] = 'homepage.settings'
    os.environ['ENABLE_LOGGING'] = 'False'
    os.environ['DEBUG'] = 'True'

    import django
    from django.test.utils import get_runner
    from django.conf import settings

    django.setup()

    # TODO: settings
    test_runner = get_runner(settings)

    test_runner = test_runner()
    failures = test_runner.run_tests(None)

    sys.exit(failures)

if __name__ == '__main__':
    main()
