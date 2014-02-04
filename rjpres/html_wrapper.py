"""HTML wrapper to use a MarkDown file with RevealJS
"""

import os.path
import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class HtmlWrapper(object):
    """Provide HTML wrapper for Markdown files for JS-Reveal
    """

    def __init__(self, base_dir, data_dir):
        self.base_dir=base_dir
        self.data_dir=data_dir

    def wrapper_url(self,url):
        """Check whether we should provide a wrapper for url, return nothing
        if not, else wrapper url
        """
        if url.endswith('.md'):
            rjp_url = url + ".html"
            return(rjp_url)
        return(None)
    
    def source_url(self,url):
        """Return markdown source url if this is a wrapper url
        
        Returns None if this isn't a wrapper url
        """
        if url.endswith('.md.html'):
            surl = url.replace('.md.html','.md')
            if os.path.exists(surl):
                return(surl)
        return(None)

    def wrapper(self,path):
        """Return StringIO object that is HTML wrapper for Markdown
        """
        template_file = os.path.join(self.base_dir,"templates","default.tpl")
        template = open(template_file).read()
        # Populate arguments for template
        args = { 'title': "TITLE_IN_HERE",
                 'md_file': os.path.basename(path) }
        # Fill template and return
        f = StringIO()        
        f.write( template.format(**args) )
        return(f)
