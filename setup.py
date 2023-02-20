from setuptools import setup, find_packages, pybuild
import __version__

setup(
    name='stf-scrape_tf2ez-pybuy',
    version=__version__,
    description='Python scraper designed to purchase items from tf2ez stock, which employs rabbitmq for communication with stf-scrape_tf2ez',
    author='Oskar Stasiak, Jason McElhenney',
    author_email='oscar@spooky.tf, jason@spooky.tf',
    url='https:gh.boo.tf/stf-scrape_tf2ez-pybuy',
    packages=find_packages(exclude=()),
    install_requires=["selenium", "setuptools", "python-dotenv", "pika", "undetected_chromedriver", "pipreqs", "pybuild", "pybuild[build]"],

)