try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='globefish',
    version='',
    packages=['globefish'],
    url='',
    license='MIT',
    author='ladder1984',
    author_email='ladder1984@gmail.com',
    description='A Python Web Framework.',
    install_requires=[
        'Jinja2>=2.4',
    ],
)
