from setuptools import setup, find_packages

setup(
    name="heart-disease-prediction",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-jwt-extended',
        'flask-cors',
        'mysql-connector-python',
    ],
) 