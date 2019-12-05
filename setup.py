from setuptools import setup, find_packages


README = open('README.rst').read()
HISTORY = open('HISTORY.rst').read().replace('.. :changelog:', '')

with open("pydiscourse/__init__.py", "r") as module_file:
    for line in module_file:
        if line.startswith("__version__"):
            version_string = line.split("=")[1]
            VERSION = version_string.strip().replace("\"", "")


setup(
    name="pydiscourse",
    version=VERSION,
    description="A Python library for the Discourse API",
    long_description=README + '\n\n' + HISTORY,
    author="Marc Sibson and contributors",
    author_email="ben+pydiscourse@benlopatin.com",
    license="BSD",
    url="https://github.com/bennylope/pydiscourse",
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=[
        'requests>=2.4.2',
    ],
    tests_require=[
        'mock',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'pydiscoursecli = pydiscourse.main:main'
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    zip_safe=False,
)
