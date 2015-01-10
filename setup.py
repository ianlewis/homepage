#:coding=utf-8:

from distutils.core import Command
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist


class BuildStatic(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Run the collectstatic django command.
        import os
        # NOTE: Enable debug mode so it doesn't complain about required
        #       settings like SECRET_KEY.
        os.environ['DEBUG'] = 'True'
        os.environ['DJANGO_SETTINGS_MODULE'] = 'homepage.settings'
        from django.core.management import call_command
        call_command('collectstatic', interactive=False)


class SdistWithBuildStatic(sdist):
    def run(self):
        self.run_command('build_static')
        return sdist.run(self)


setup(
    name="homepage",
    version="0.0.1",
    author="Ian Lewis",
    author_email="ianmlewis@gmail.com",
    description="Ian Lewis' homepage at www.ianlewis.org",
    license="MIT",
    keywords="django homepage blog",
    url="http://www.ianlewis.org/",
    packages=find_packages(),
    long_description="",  # TODO: Readme
    cmdclass={
        'build_static': BuildStatic,
        'sdist': SdistWithBuildStatic,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: MIT License",
    ],
)
