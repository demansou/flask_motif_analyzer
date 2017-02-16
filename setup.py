from setuptools import setup

setup(
    name='motif_analyzer',
    packages=[
        'motif_analyzer',
    ],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_pymongo',
        'numpy',
        'biopython',
        'celery',
    ],
)
