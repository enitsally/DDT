from setuptools import setup, find_packages, Command

setup(
    name='ddt',
    description='',
    version='0.0.1',
    packages=find_packages(),
    #package_data={'': ['airflow/alembic.ini']},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'pymongo',
        'pandas',
        'gunicorn',
        'flask-cors',
        'SQLAlchemy',
        'sqlalchemy-redshift',
        'pyodbc',
        'psycopg2'
    ],
    extras_require={
    },
    author='Yue Ming',
    author_email='yue.ming@wdc.com',
    url='http://yue.ming',
)
