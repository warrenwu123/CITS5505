from setuptools import setup, find_packages

setup(
    name='fitness-tracker',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask>=3.1.0',
        'flask-sqlalchemy>=3.1.1',
        'flask-migrate>=4.0.4',
        'flask-login>=0.6.3',
        'flask-wtf>=1.2.2',
        'flask-mail>=0.10.0',
        'email-validator>=2.2.0',
        'psycopg2-binary>=2.9.10',
        'gunicorn>=23.0.0',
        'qrcode>=8.1',
        'pyotp>=2.9.0',
        'sqlalchemy>=2.0.40',
        'werkzeug>=3.1.3',
        'wtforms>=3.2.1',
    ],
    extras_require={
        'test': [
            'pytest==7.4.3',
            'pytest-cov==4.1.0',
            'pytest-flask==1.3.0',
        ],
    },
) 