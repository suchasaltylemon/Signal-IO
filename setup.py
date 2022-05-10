from setuptools import setup, find_packages

setup(
    name="signalio",
    version="1.0.4",
    description="A simple Python networking package",
    url="https://github.com/suchasaltylemon/Signal-IO",
    author="SuchASaltyLemon",
    author_email="suchasaltylemon@mailbox.org",
    packages=find_packages("src"),
    package_dir={"": "src"}
)
