from setuptools import (
    find_packages,
    setup
)

setup(
    name = "crate-signature",
    version = "0.1.0",
    packages = find_packages(include=["crate_signature", "crate_signature.*"]),
    install_requires = ["setuptools", "cryptography"],
    entry_points = {"console_scripts": ["crate-signature=crate_signature.main:main"]}
)
