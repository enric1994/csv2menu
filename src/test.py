import unittest
from app import is_true, format_price


class TestStringMethods(unittest.TestCase):

    def test_is_true(self):
        """ Test is_true function """

        self.assertEqual(is_true('YES'), True)
        self.assertEqual(is_true('yes'), True)
        self.assertEqual(is_true('Yes'), True)
        self.assertEqual(is_true('Y'), True)
        self.assertEqual(is_true('y'), True)
        self.assertEqual(is_true('SÍ'), True)
        self.assertEqual(is_true('si'), True)
        self.assertEqual(is_true('oui'), True)
        self.assertEqual(is_true('NO'), False)
        self.assertEqual(is_true('No'), False)
        self.assertEqual(is_true('Something'), False)

    def test_format_price(self):
        """ Test format_price function """

        self.assertEqual(format_price(123), '123')
        self.assertEqual(format_price('123'), '123')
        self.assertEqual(format_price(123.99), '123.99')
        self.assertEqual(format_price(123.99999999), '124')
        self.assertEqual(format_price('123.5'), '123.50')
        self.assertEqual(format_price('123.5EURO'), '123.50')
        self.assertEqual(format_price('123.5€'), '123.50')
        self.assertEqual(format_price('123.5 €'), '123.50')
        self.assertEqual(format_price('€€€€123.5€€€'), '123.50')


if __name__ == '__main__':
    unittest.main()