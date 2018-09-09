from setuptools import setup, find_packages

install_requires = [
    'jinja2',
    'pypandoc',
    'click',
    'pandas',
    'yaml'
    ]

setup(
    name="figurator",
    version="0.1",
    long_description=__doc__,
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=True,
    entry_points="""
        [console_scripts]
        figurator=figurator.cli:cli
    """
)
