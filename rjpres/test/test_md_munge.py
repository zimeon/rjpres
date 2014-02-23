"""
"""
import re
import sys
import unittest
import StringIO
from rjpres.md_munge import MdMunge

class TestExamplesFromSpec(unittest.TestCase):

    def test01_no_rjs_markdown(self):
        test_strings = ['',
                        '# title\n\nsome text\nend\n',
                        'stuff\n --- indented\n',
                        'stuff\n *** indented\n'
                        ]
        for mdstr in test_strings:
            fh=StringIO.StringIO(mdstr)
            mdm = MdMunge()
            self.assertFalse(mdm.md_has_rjs_markup(fh))

    def test02_with_rjs_markdown(self):
        test_strings = ['---',
                        '***',
                        '---- and anything else\ndsjfk\n',
                        '**** and anything else\ndsjfk\n',
                        'stuff\nstuff\n**** and anything else\ndsjfk\n',
                        'stuff\nstuff\n---* and anything else\ndsjfk\n'
                        ]
        for mdstr in test_strings:
            fh=StringIO.StringIO(mdstr)
            mdm = MdMunge()
            self.assertTrue(mdm.md_has_rjs_markup(fh))

    def test03_munge(self):
        src = '# Title\n\ncontent\n\n## Sub1\n\nblah\n\n# Title2\n\nblah\n'
        dst = '# Title\n\ncontent\n\n***\n\n## Sub1\n\nblah\n\n---\n\n# Title2\n\nblah\n'
        fh=StringIO.StringIO(src)
        f = MdMunge().munge(fh)
        f.seek(0)
        out = f.read()
        self.assertEqual(out, dst)

    def test04_ex2_to_ex3(self):
        ex2_file = 'examples/pres2_no_pages.md'
        ex3_file = 'examples/pres3_from_pres2.md'
        #
        ex2_fh = open( ex2_file, 'rb' )
        mdm = MdMunge()
        sio = mdm.md_needs_munge(ex2_fh)
        self.assertTrue( sio is not None )
        self.assertTrue( sio )
        sio.seek(0)
        ex2_munged = sio.read()
        ex3 = open( ex3_file, 'rb' ).read()
        self.assertEqual( ex2_munged, ex3 )
