"""
This is an example implementation of the SolrSitemap class. The purpose
is to demonstrate how to extend or override the parent class to
manipulate the search results as required.

"""
import datetime
from solrsitemap import SolrSitemap

from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from myapp.search_backend import MySearchQuerySet


class MySolrSitemap(SolrSitemap):
    """
    SolrSitemap subclass for building a sitemap for a bookstore
    website.
    
    """
    def __init__(self, datefilter=None, queryclass=MySearchQuerySet, **kwargs):
        if datefilter is None:
            datefilter = datetime.date.today()
            
        self.datefilter = datefilter
        super(MySolrSitemap, self).__init__(queryclass=queryclass, **kwargs)
        
    def _sqs(self):
        sqs = super(MySolrSitemap, self)._sqs()._clone()
        return sqs.filter(date_published=self.datefilter).values('title',
                                                                 'author')

    def items(self):
        """
        Take the values in the 'title' and 'author' fields and slugify
        them. These slugified values will be used in the URL.
        
        """
        # This is going to be a list of dictionaries because we used .values
        # in the '_sqs' method.
        results = super(MySolrSitemap, self).items()
        items = []
        
        for result in results:
            items.append(dict((k, slugify(v)) for k, v in result.items()))
            
        return items

    def location(self, obj):
        # 'obj' will be one of the elements from the list returned by the
        # 'items' method. In this example, that means it is a dictionary that
        # looks like:
        #
        # {'title': 'around-the-world-in-80-days', 'author': 'jules-verne'}
        #
        # so we'll pass it to 'reverse' to generate our URL string.
        # It should look something like
        # '/jules-verne/around-the-world-in-80-days/'
        return reverse('someview', kwargs=obj)
        
