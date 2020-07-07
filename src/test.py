import unittest
from utils import is_true, format_price, format_calories, format_suitable, format_allergens, format_euro


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

        self.assertEqual(format_price(123), '123.00')
        self.assertEqual(format_price('123'), '123.00')
        self.assertEqual(format_price(123.99), '123.99')
        self.assertEqual(format_price(123.99999999), '124.00')
        self.assertEqual(format_price('123.5'), '123.50')
        self.assertEqual(format_price('123.5EURO'), '123.50')
        self.assertEqual(format_price('123.5€'), '123.50')
        self.assertEqual(format_price('123.5 €'), '123.50')
        self.assertEqual(format_price('€€€€123.5€€€'), '123.50')

    def test_format_calores(self):
        """ Test format_calories function """

        self.assertEqual(format_calories(123), '123 kCal')
        self.assertEqual(format_calories(123.49), '123 kCal')
        self.assertEqual(format_calories(123.50), '124 kCal')
        self.assertEqual(format_calories(123.99999), '124 kCal')
        self.assertEqual(format_calories('123'), '123 kCal')
        self.assertEqual(format_calories('123.50'), '124 kCal')
        self.assertEqual(format_calories('123.99999'), '124 kCal')
        self.assertEqual(format_calories('123.5kCal'), '124 kCal')
        self.assertEqual(format_calories('123.5 kCal'), '124 kCal')
        self.assertEqual(format_calories('kCalkCal123.5kCal'), '124 kCal')
        self.assertEqual(format_calories('0'), '')
        self.assertEqual(format_calories(-5), '')

    def test_format_suitable(self):
        """ Test format_suitable function """

        item = { 'vegetarian': 'yes', 'vegan': 'yes' }
        self.assertEqual(format_suitable(item), '(V, Ve)')
        item = { 'vegetarian': 'yes', 'vegan': 'no' }
        self.assertEqual(format_suitable(item), '(V)')
        item = { 'vegetarian': 'no', 'vegan': 'yes' }
        self.assertEqual(format_suitable(item), '(Ve)')
        item = { 'vegetarian': 'no', 'vegan': 'no' }
        self.assertEqual(format_suitable(item), '')

    def test_format_allergens(self):
        """ Test format_allergens function """

        item = { 
            'allergen_gluten': 'yes',
            'allergen_crustaceans': 'no',
            'allergen_eggs': 'no',
            'allergen_fish': 'no',
            'allergen_peanuts': 'no',
            'allergen_soybeans': 'no',
            'allergen_milk': 'no',
            'allergen_nuts': 'no',
            'allergen_celery': 'no',
            'allergen_mustard': 'no',
            'allergen_sesame': 'no',
            'allergen_sulphites': 'no',
            'allergen_lupin': 'no',
            'allergen_molluscs': 'no',
        }
        self.assertEqual(format_allergens(item), '<span> <strong>G:</strong> Gluten </span>')
        item = { 
            'allergen_gluten': 'yes',
            'allergen_crustaceans': 'yes',
            'allergen_eggs': 'no',
            'allergen_fish': 'no',
            'allergen_peanuts': 'no',
            'allergen_soybeans': 'no',
            'allergen_milk': 'no',
            'allergen_nuts': 'no',
            'allergen_celery': 'no',
            'allergen_mustard': 'no',
            'allergen_sesame': 'no',
            'allergen_sulphites': 'no',
            'allergen_lupin': 'no',
            'allergen_molluscs': 'no',
        }
        self.assertEqual(format_allergens(item), 
            '<span> <strong>G:</strong> Gluten </span><br><span> <strong>C:</strong> Crustaceans </span>')

    def test_format_euro(self):
        """ Test format_calories function """

        self.assertEqual(format_euro('€'), '&euro;')
        self.assertEqual(format_euro('123€'), '123&euro;')


if __name__ == '__main__':
    unittest.main()