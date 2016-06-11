from setuptools import setup, find_packages

requirements = [
    "youtube-dl",
    "Flask",
    "mutagen",
]

setup(
    name='icystream',
    version='0.1',
    packages=find_packages(),
    url='http://www.sighalt.de',
    license='GPLv3',
    author='sighalt',
    author_email='admin@sighalt.de',
    description='A quick and dirty SHOUTcast server streaming audio from '
                'YouTube',
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "icystream = icystream.commands:startup",
        ]
    }
)
