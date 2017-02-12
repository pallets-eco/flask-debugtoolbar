import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''


setup(
    name='Flask-DebugToolbar',
    version='0.10.1',
    url='https://flask-debugtoolbar.readthedocs.io/',
    license='BSD',
    author='Michael van Tellingen',
    author_email='michaelvantellingen@gmail.com',
    maintainer='Matt Good',
    maintainer_email='matt@matt-good.net',
    description='A toolbar overlay for debugging Flask applications.',
    long_description=README + '\n\n' + CHANGES,
    zip_safe=False,
    platforms='any',
    include_package_data=True,
    packages=['flask_debugtoolbar',
              'flask_debugtoolbar.panels'
    ],
    install_requires=[
        'Flask>=0.8',
        'Blinker',
        'itsdangerous',
        'werkzeug',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
