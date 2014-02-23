"""Munge Markdown to make it work better with rjpres 
"""

import os.path
import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class MdMunge(object):
    """Munge Markdown to make it work better with rjpres 
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def md_needs_munge(self,md):
        """Look at markdown to see whether munge is necessary

        If munge is necessary then return a StingIO object with munged
        version, else None
        """
        if (self.md_has_rjs_markup(md)):
            return None
        return self.munge(md)

    def md_has_rjs_markup(self,md):
        """Does it look like we should munge?

        FIXME - better testing, should we use proper Markdown parser?
        
        FIXME - perhaps should only look at first 100 lines or something
        in case of large document
        """
        for line in md.readlines():
            m = re.match("(\*\*\*|\-\-\-)",line)
            if (m):
                md.seek(0)
                return(True)
        md.seek(0)
        return(False)

    def munge(self,md):
        """Return StringIO object that is munged Markdown
        
        Add horizontal and vertical page breaks before level 1 and
        level 2 headings respectively. Requires Reveal-JS to be set
        up with --- as horizontal and *** as vertical pagebreak.
        """
        # Create StringIO() object with modified content
        f = StringIO()        
        seen_heading = False
        for line in md.readlines():
            m = re.match("(#{1,2})\s",line)
            if (m):
                if (m.group(1)=='#' and seen_heading):
                    # have level 1 heading
                    f.write("---\n\n")
                elif (m.group(1)=='##' and seen_heading):
                    # have level 1 heading
                    f.write("***\n\n")
                seen_heading = True
            f.write(line)
        md.close()
        return(f)
