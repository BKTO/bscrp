from distutils.core import setup

setup(
  name = 'bscrp',
  packages = ['bscrp'],
  package_dir = {'bscrp': 'bscrp'},
  package_data = {'bscrp': ['*']},
  version = '0.5',
  description = 'Better Scrape, a collection of open source scraping methods used by Better Know The Opposition',
  author = 'BKTO',
  author_email = 'hello@betterknowtheopposition.com',
  url = 'https://github.com/BKTO/bscrp',
  download_url = 'https://github.com/BKTO/bscrp',
  keywords = ['scraping'],
  classifiers = [],
)
