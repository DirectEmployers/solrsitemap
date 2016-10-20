import math
try:
    from django.contrib.sites.models import Site, get_current_site
except ImportError:
    from django.contrib.sites.models import Site
    from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sitemaps import Sitemap
from haystack.query import SearchQuerySet


class SolrSitemap(Sitemap):
    """
    Skeleton class to generate sitemaps based on data from a Solr index.

    This sitemap is "lazy" compared to Django's built-in Sitemap, in that
    it does not fetch the data needed to compute all the URLs at once.
    Instead of using Django's built-in pagination, we delegate pagination
    operations to Solr itself using its `start` and `rows` parameters.
    
    """
    def __init__(self, page=1, queryclass=SearchQuerySet):
        self.pagenum = page
        self.queryclass = queryclass
        self.results = self._sqs()._clone()
        
    def _sqs(self):
        """
        Returns the base query result set on which the rest of the
        sitemap-generation operations will be based. Any subclasses of
        this class will likely want to override this method with their
        own logic.

        For example, if you have your URL data in the 'location' and
        'title' fields, you would want to do something like:

        return self.queryclass().values('location_slug', 'title_slug')
        
        """
        return self.queryclass()
    
    def numpages(self):
        # Return the number of pages it will take to display all results. Of
        # course we'll need to round up if the number of results isn't evenly
        # divisible by self.limit, ergo ``math.ceil()``.
        ct = float(self.results._clone().count())
        return int(math.ceil(ct/self.limit))

    def lastmod(self, obj):
        return datetime.datetime.utcnow()

    def get_urls(self, site=None):
        if site is None:
            if Site._meta.installed:
                try:
                    site = Site.objects.get_current()
                except Site.DoesNotExist:
                    pass
            if site is None:
                raise ImproperlyConfigured("""In order to use Sitemaps you must\
                                            either use the sites framework or\
                                            pass in a Site or RequestSite\
                                            object in your view code.""")

        urls = []
        # This is where the `get_urls` deviates from the built-in `Sitemap`
        # class; there, the paginator is called on the next line. Instead,
        # the `items` method only gets enough results to populate a single page.
        for item in self.items():
            loc = "http://%s%s" % (site.domain, self.location(item))
            priority = self.priority(item)
            url_info = {
                'location':   loc,
                'lastmod':    self.lastmod(item),
                'changefreq': self.changefreq(item),
                'priority':   str(priority is not None and priority or '')
            }
            urls.append(url_info)
        return urls
    
    def items(self):
        """
        Return a SearchQuerySet, the range of which is determined by
        `self.pagenum` and `self.limit`.

        It is likely that a subclass will need to extend this method to
        convert the Haystack SearchResult instances to an object type --
        probably `dict` -- that implements the API their sitemap-related
        methods (e.g. `location`, `lastmod`) will use.

        I've left it alone here so overriding can be as simple as:

        class MySolrSitemap(SolrSitemap):
            def items(self):
                results = super(MySolrSitemap, self).items()
                return [result.get_stored_fields() for result in results]

        """
        end = int(self.pagenum) * self.limit
        start = end - self.limit
        return self.results[start:end]

    def location(self, obj):
        """
        Inputs:
        `obj`: A single object from the collection of objects returned by
        the `items` method.

        Returns:
        An absolute path to the object. This is the path component of the
        URI that will be displayed in the sitemap.
        
        """
        raise NotImplementedError

