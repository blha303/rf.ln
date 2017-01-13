from setuptools import setup

setup(
    name='rfln',
    packages=['rfln'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy',
    ],
)
