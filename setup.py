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


install_requires = [
    'Django==1.4.20',
    'South==0.7.6',

    # For rendering blog posts
    'docutils>=0.5',
    'pygments>=1.0',
    'html2text==3.200.3',
    'Markdown==2.6',

    # For thumbnails
    'Pillow==2.5.1',

    # Filebrowser admin.
    'django-filebrowser-no-grappelli==3.5.7',

    # Pagination
    'django-pagination==1.0.7',

    # Settings
    'django-constance[database]==1.0.1',

    # Comments
    'django-disqus==0.4.3',

    # Static files
    'django-compressor==1.4',
    'dj-static==0.0.6',

    # Production
    'meinheld==0.5.7',
    'MySQL-python==1.2.3',
    'pylibmc==1.4.1',
]

setup(
    name="homepage",
    version="0.1.1",
    author="Ian Lewis",
    author_email="ianmlewis@gmail.com",
    description="Ian Lewis' homepage at www.ianlewis.org",
    license="MIT",
    keywords="django homepage blog",
    url="http://www.ianlewis.org/",
    packages=find_packages(),
    long_description=open('README.md').read(),
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
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: MIT License",
    ],
)
