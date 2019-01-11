from io import open

from setuptools import setup

# python setup.py sdist --formats=zip
# python setup.py sdist bdist_wheel
# twine upload dist/halolib-0.13.8.tar.gz -r pypitest

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='halolib',
    version='0.14.8',
    packages=['halolib', 'halolib.flask'],
    url='https://github.com/yoramk2/halolib',
    license='MIT License',
    author='yoramk2',
    author_email='yoramk2@yahoo.com',
    description='this is the Halo framework library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
