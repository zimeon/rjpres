"""HTTP Server for rjpres

This module builds on SimpleHTTPServer by adding extra functionality
to deal with serving files from two directory trees (the user's dir 
and a static data dir), dynamically providing wrapper pages, and
processing Markdown files that perhaps weren't orginally designed 
for presentation with Reveal-JS.
"""

from _version import __version__
__all__ = ["SimpleHTTPRequestHandler"]

import os
import posixpath
import SimpleHTTPServer
import urllib
import cgi
import re
import sys
import shutil
import mimetypes
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from rjpres.md_munge import MdMunge

class RjpresHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    # Class variables used for a number of configurations used each
    # time this handler is instantiated
    server_version = "SimpleHTTP+rjpres/" + __version__
    #protocol_version ... HTTP protocol, no need to override
    #wrapper ... request wrapper
    #base_dir ... base dir of files to serve
    #data_dir ... dir of local data with RevealJS etc
    allow_from = None #set to list of IP regexs to allow access from

    def do_GET(self, is_head=False):
        """Serve a GET request (or HEAD by truncating)
        
        The HEAD response is identical to GET except that no
        content is sent, could likely be optimized.
        """
        if (not self.check_access()):
            return
        path = self.check_path()
        f = self.send_head(path)
        if f:
            if (not is_head):
                self.copyfile(f, self.wfile)
                f.close()

    def do_HEAD(self):
        """Serve a HEAD request

        All this does is call do_GET with the flag is_head set to do
        everything except actually sending content
        """
        self.do_GET(is_head=True)

    def check_access(self):
        """Should we answer this request? Send error and respond False if not

        If we wanted to be more brutal and simply not answer then this 
        could be done via override of superclass verify_request(). However,
        will answer this with a 403 so do it in HTTP.

        FIXME - should implement something based on the dotted IP notation

        FIXME - should work with numeric IPs (left partfirst) and resolved
        IP (right part first, currently not implemented)
        """
        if (self.allow_from is None):
            return True
        # have access control list
        remote_host = self.client_address[0]
        for pattern in self.allow_from:
            if (re.match(pattern,remote_host)):
                return True
        # no match => not allowed
        self.send_error(403)
        return False

    def check_path(self):
        """Check path requested and work out whether we'll make a substitution

        If self.path corresponds with a file in the server context the
        simply return that, else look for package data that matches the
        path. In the case that neither match then return the unmodified
        path so that when used it generates an understandable error.
        """
        path = self.translate_path(self.path)
        local_path = os.path.join(self.base_dir,path)
        data_path = os.path.join(self.data_dir,path)
        if (os.path.exists(local_path)):
            # All good, serve file requested
            return(local_path)
        elif (os.path.exists(data_path)):
            # We have this as part of module data
            self.log_message("serving %s from module data" % (data_path))
            return(data_path)
        else:
            # Fall back on usual 404 etc.
            return(local_path)

    def send_head(self,path):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        sio = None
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
            # Is this a markdown file which needs to be processed first?
            wurl = self.wrapper.wrapper_url(path)
            if (wurl):
                mdm = MdMunge()
                sio = mdm.md_needs_munge(f)
                if (sio):
                    self.log_message("have processed markdown for %s" % (path))
        except IOError:
            # Should we generate a dynamic wrapper?
            surl = self.wrapper.source_url(path)
            if (surl):
                sio = self.wrapper.wrapper(surl)
                self.log_message("have generated wrapped for %s" % (surl))
            else:
                self.send_error(404, "File not found")
                return None
        # Now expect to have either valid sio stream else valid f
        if (sio):
            self.send_head_from_stringio(sio)
            return sio
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n')
        f.write("<html>\n<head>\n")
        f.write("<title>Directory listing for %s</title>\n" % displaypath)
        f.write('<link rel="stylesheet" href="/css/rjpres.css">\n</head<\n>')
        f.write("<body>\n")
        presentations = []
        files = []
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            wurl = self.wrapper.wrapper_url(name)
            if (wurl):
                files.append(
                    '<li class="markdown"><a href="%s" alt="raw markdown">%s</a></li>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
                presentations.append(
                    '<li class="pres"><a href="%s" alt="presentation">Presentation of %s</a></li>\n'
                    % (urllib.quote(wurl), cgi.escape(displayname)))
            else:
                files.append(
                    '<li><a href="%s">%s</a></li>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        # Write sections with entries...
        if (len(presentations)>0):
            f.write("<h2>Presentations</h2>\n")
            f.write("<ul>\n")
            f.write(''.join(presentations))
            f.write("</ul>\n\n")
        if (len(files)>0):
            f.write("<h2>Directory listing for %s</h2>\n" % displaypath)
            f.write("<ul>\n")
            f.write(''.join(files))
            f.write("</ul>\n")
        f.write("</body>\n</html>\n")
        self.send_head_from_stringio(f)
        return f

    def send_head_from_stringio(self,f):
        """Write HTTP HEAD from StringIO, leaving f ready to copy contents

        Note: expects f to be at end so that tell() works to get length
        """
        length = f.tell()
        f.seek(0)
        encoding = sys.getfilesystemencoding()
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        Returns a relative path that should be interpretted in the
        server's context.
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = '' #os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            if (path==''):
                path = word
            else:
                path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })
