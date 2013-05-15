from parsley_json import JSONParser
import unittest

class JSONParserTests(unittest.TestCase):


    def test_integer(self):
        self.assertEqual(JSONParser("123").number(), 123)
        self.assertEqual(JSONParser("-123").number(), -123)
        self.assertEqual(JSONParser("0").number(), 0)

    def test_float(self):
        self.assertEqual(JSONParser("0.5").number(), 0.5)
        self.assertEqual(JSONParser("1.0").number(), 1.0)
        self.assertEqual(JSONParser("-3.5").number(), -3.5)
        self.assertEqual(JSONParser("2e7").number(), 2e7)
        self.assertEqual(JSONParser("1.2E6").number(), 1.2E6)

    def test_string(self):
        self.assertEqual(JSONParser('u2603').escapedUnicode(), u"\u2603")
        self.assertEqual(JSONParser('"foo"').string(), u"foo")
        self.assertEqual(JSONParser(r'"foo\n"').string(), u"foo\n")
        self.assertEqual(JSONParser(r'"foo\rbaz\u2603"').string(), u"foo\rbaz\u2603")
        self.assertEqual(JSONParser(r'"\\\/\b\"\f\t"').string(), u'\\/\b"\f\t')

    def test_literals(self):
        self.assertEqual(JSONParser(r'true').value(), True)
        self.assertEqual(JSONParser(r'false').value(), False)
        self.assertEqual(JSONParser(r'null').value(), None)

    def test_array(self):
        self.assertEqual(JSONParser(r'[1, 2]').array(), [1, 2])
        self.assertEqual(JSONParser(r'["foo", []]').array(), ["foo", []])

    def test_object(self):
        self.assertEqual(JSONParser(r'{"foo": 1}').object(), {"foo": 1})
        self.assertEqual(JSONParser(r'{"foo": "baz", "x": {}}').object(),
                         {"foo": "baz", "x": {}})

