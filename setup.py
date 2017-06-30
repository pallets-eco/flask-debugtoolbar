import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except Exception:
    README = ''
    CHANGES = ''


install_requires = [
    'Flask>=0.8',
    'Blinker',
    'itsdangerous',
    'werkzeug',
],

tests_require = [
    'pytest>=3.0.5',
    'Flask-SQLAlchemy'
]

extras_require = {
    'tests': tests_require,
}

setup_requires = [
    'pytest-runner>=2.6.2'
]

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)


setup(
    name='Flask-DebugToolbar',
    version='0.12.dev0',
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
    packages=[
        'flask_debugtoolbar',
        'flask_debugtoolbar.panels'
    ],
    extras_require=extras_require,
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
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
