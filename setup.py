from setuptools import setup

setup(
    name='motif_analyzer',
    packages=[
        'motif_analyzer',
    ],
    include_package_data=True,
    install_requires=[
        'Flask>=0.12',
        'Flask-PyMongo>=0.4.1',
        'Jinja2>=2.9.4',
        'MarkupSafe>=0.23',
        'Werkzeug>=0.11.15',
        'amqp>=2.1.4',
        'billiard>=3.5.0.2',
        'biopython>=1.68',
        'celery=4.0.2',
        'click>=6.7',
        'itsdangerous>=0.24',
        'kombu>=4.0.2',
        'pip>=9.0.1',
        'pymongo>=3.4.0',
        'pytz>=2016.10',
        'setuptools>=18.1',
        'six>=1.10.0',
        'vine>=1.1.3',
    ],
)
