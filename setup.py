from distutils.core import setup

setup(
    name = "solrsitemap",
    version = "1.0",
    description = "Tool to generate sitemaps using Django Haystack & Solr",
    author = "Matt DeBoard",
    author_email = "matt@directemployersfoundation.org",
    long_description = open('README.rst', 'r').read(),
    py_modules = ['solrsitemap'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
    ],
    url = 'http://github.com/DirectEmployers/solrsitemap/'
)
