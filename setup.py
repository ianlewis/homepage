#:coding=utf-8:

import os

from distutils.core import Command
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist

BASE_PATH = os.path.dirname(__file__)


class BuildStatic(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Run the collectstatic django command.
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


with open(os.path.join(BASE_PATH, 'requirements.txt')) as requirements:
    install_requires = []
    for line in requirements.readlines():
        line = line.strip()
        if line and not line.startswith("#"):
            install_requires.append(line)

setup(
    name="homepage",
    version="0.1.15",
    author="Ian Lewis",
    author_email="ianmlewis@gmail.com",
    description="Ian Lewis' homepage at www.ianlewis.org",
    license="MIT",
    keywords="django homepage blog",
    url="http://www.ianlewis.org/",
    packages=find_packages(),
    long_description=open(os.path.join(BASE_PATH, 'README.md')).read(),
    install_requires=install_requires,
    include_package_data=True,  # Include static files, templates, etc.
    cmdclass={
        'build_static': BuildStatic,
        'sdist': SdistWithBuildStatic,
    },
    entry_points={
        'console_scripts': [
            'homepage = homepage.runner:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7"
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Framework :: Django :: 1.4",
        "License :: OSI Approved :: MIT License",
    ],
)
