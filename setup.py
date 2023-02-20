from setuptools import setup, find_packages


setup(
    name='stf-scrape_tf2ez-pybuy',
    version='1.5.0',
    description='Python scraper designed to purchase items from tf2ez stock, which employs rabbitmq for communication with stf-scrape_tf2ez',
    author='Oskar Stasiak, Jason McElhenney',
    author_email='oscar@spooky.tf, jason@spooky.tf',
    url='https:gh.boo.tf/stf-scrape_tf2ez-pybuy',
    packages=find_packages(exclude=())
)