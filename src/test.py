import unittest
from utils import is_true, format_price, format_calories, format_suitable, format_allergens


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
            'allergy_gluten': 'yes',
            'allergy_crustaceans': 'no',
            'allergy_eggs': 'no',
            'allergy_fish': 'no',
            'allergy_peanuts': 'no',
            'allergy_soybeans': 'no',
            'allergy_milk': 'no',
            'allergy_nuts': 'no',
            'allergy_celery': 'no',
            'allergy_mustard': 'no',
            'allergy_sesame': 'no',
            'allergy_sulphites': 'no',
            'allergy_lupin': 'no',
            'allergy_molluscs': 'no',
        }
        self.assertEqual(format_allergens(item), '<span> G: Gluten </span>')
        item = { 
            'allergy_gluten': 'yes',
            'allergy_crustaceans': 'yes',
            'allergy_eggs': 'no',
            'allergy_fish': 'no',
            'allergy_peanuts': 'no',
            'allergy_soybeans': 'no',
            'allergy_milk': 'no',
            'allergy_nuts': 'no',
            'allergy_celery': 'no',
            'allergy_mustard': 'no',
            'allergy_sesame': 'no',
            'allergy_sulphites': 'no',
            'allergy_lupin': 'no',
            'allergy_molluscs': 'no',
        }
        self.assertEqual(format_allergens(item), 
            '<span> G: Gluten </span><br><span> C: Crustaceans </span>')


if __name__ == '__main__':
    unittest.main()