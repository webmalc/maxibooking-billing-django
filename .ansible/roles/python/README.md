# ansible-python

[Python](https://www.python.org/) - Python is a programming language that lets you work quickly and integrate systems more effectively.

[![Build Status](https://travis-ci.org/telusdigital/ansible-python.svg?branch=master)](https://travis-ci.org/telusdigital/ansible-python)
[![Platforms](http://img.shields.io/badge/platforms-ubuntu-lightgrey.svg?style=flat)](#)

Description
-----------
 > Python is a widely used general-purpose, high-level programming language. Its design philosophy emphasizes code readability, and its syntax allows programmers to express concepts in fewer lines of code than would be possible in languages such as C++ or Java. The language provides constructs intended to enable clear programs on both a small and large scale.
>
> Python supports multiple programming paradigms, including object-oriented, imperative and functional programming or procedural styles. It features a dynamic type system and automatic memory management and has a large and comprehensive standard library.
> -- Wikipedia entry for Python

Tunables
--------
* ```python_packages``` (list) - Packages to install with pip
* ```python_build_dependencies``` (string) - Build dependencies for packages (will be installed with apt)
* ```python_requirements_file``` (string) - A requirements.txt file listing all dependencies.
* ```python_legacy_support``` (string) - Use Python 2.x?
* ```python_pip_executable``` (string) - Path to ```pip``` executable.

Dependencies
------------
* None

Example Playbook
----------------
    - hosts: servers
      roles:
         - role: telusdigital.python
           python_packages:
             - awscli
             - boto
         - role: telusdigital.python
           python_legacy_support: yes
           python_packages:
             - ansible

License
-------
[MIT](https://tldrlegal.com/license/mit-license)

Contributors
------------
* [Chris Olstrom](https://colstrom.github.io/) | [e-mail](mailto:chris@olstrom.com) | [Twitter](https://twitter.com/ChrisOlstrom)
* Steven Harradine
* Nikki
* Alex Podobnik
