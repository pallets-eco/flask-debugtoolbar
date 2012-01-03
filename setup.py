from setuptools import setup, find_packages


setup(
    name='Flask-DebugToolbar',
    version='0.6dev',
    url='http://github.com/mvantellingen/flask-debugtoolbar',
    license='BSD',
    author='Michael van Tellingen',
    author_email='michaelvantellingen@gmail.com',
    description='A port of the Django debug toolbar to Flask',
    long_description=__doc__,
    zip_safe=False,
    platforms='any',
    include_package_data=True,
    packages=['flask_debugtoolbar',
              'flask_debugtoolbar.panels'
    ],
    install_requires=[
        'setuptools',
        'Flask>=0.8',
        'Blinker',
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
