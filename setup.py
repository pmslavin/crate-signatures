from setuptools import setup, find_packages

setup(
    name = "crate-signature",
    version = "0.1.0",
    packages = find_packages(include=["crate_signature", "crate_signature.*"]),
    install_requires = ["setuptools"],
    entry_points = {"console_scripts": ["crate-signature=crate_signature.main:main"]}
)
