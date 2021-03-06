import unittest
from bottle import send_file, static_file, HTTPError, HTTPResponse, request, response, parse_date, Bottle
import wsgiref.util
import os
import os.path
import tempfile
import time

class TestDateParser(unittest.TestCase):
    def test_rfc1123(self):
        """DateParser: RFC 1123 format"""
        ts = time.time()
        rs = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(ts))
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_rfc850(self):
        """DateParser: RFC 850 format"""
        ts = time.time()
        rs = time.strftime("%A, %d-%b-%y %H:%M:%S GMT", time.gmtime(ts))
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_asctime(self):
        """DateParser: asctime format"""
        ts = time.time()
        rs = time.strftime("%a %b %d %H:%M:%S %Y", time.gmtime(ts))
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_bad(self):
        """DateParser: Bad format"""
        self.assertEqual(None, parse_date('Bad 123'))


class TestSendFile(unittest.TestCase):
    def setUp(self):
        e = dict()
        wsgiref.util.setup_testing_defaults(e)
        b = Bottle()
        request.bind(e, b)
        response.bind(b)

    def test_valid(self):
        """ SendFile: Valid requests"""
        out = static_file(os.path.basename(__file__), root='./')
        self.assertEqual(open(__file__,'rb').read(), out.output.read())

    def test_invalid(self):
        """ SendFile: Invalid requests"""
        self.assertEqual(404, static_file('not/a/file', root='./').status)
        f = static_file(os.path.join('./../', os.path.basename(__file__)), root='./views/')
        self.assertEqual(401, f.status)
        try:
            fp, fn = tempfile.mkstemp()
            os.chmod(fn, 0)
            self.assertEqual(401, static_file(fn, root='/').status)
        finally:
            os.close(fp)
            os.unlink(fn)
            
    def test_mime(self):
        """ SendFile: Mime Guessing"""
        f = static_file(os.path.basename(__file__), root='./')
        self.assertTrue(f.header['Content-Type'] in ('application/x-python-code', 'text/x-python'))
        f = static_file(os.path.basename(__file__), root='./', mimetype='some/type')
        self.assertEqual('some/type', f.header['Content-Type'])
        f = static_file(os.path.basename(__file__), root='./', guessmime=False)
        self.assertEqual('text/plain', f.header['Content-Type'])

    def test_ims(self):
        """ SendFile: If-Modified-Since"""
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        self.assertEqual(304, static_file(os.path.basename(__file__), root='./').status)
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))
        self.assertEqual(open(__file__,'rb').read(), static_file(os.path.basename(__file__), root='./').output.read())

    def test_download(self):
        """ SendFile: Download as attachment """
        basename = os.path.basename(__file__)
        f = static_file(basename, root='./', download=True)
        self.assertEqual('attachment; filename=%s' % basename, f.header['Content-Disposition'])
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))
        f = static_file(os.path.basename(__file__), root='./')
        self.assertEqual(open(__file__,'rb').read(), f.output.read())


if __name__ == '__main__':
    unittest.main()

