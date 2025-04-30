from setuptools import setup, find_packages

setup(
    name="apispec_generator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    python_requires=">=3.6",
    author="AIBasic",
    author_email="example@example.com",
    description="API specification generator for user stories",
)