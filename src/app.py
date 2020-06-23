# imports
import os
import io
import sys
import csv
import pandas as pd
import re

from os.path import join, abspath, dirname
from html import escape
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from collections import defaultdict

# APP
app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is my secret key!'


# Static path
STATIC_PATH = abspath(join(dirname(abspath(__file__)), "static"))
CSS_FILEPATH = join(STATIC_PATH, 'css', 'style.css')
ICONS_FILEPATH = '../src/static/icons'
OUTPUT_PATH = "/output/"


@app.route('/menu', methods=['GET', 'POST'])
def generate_menu():
    """ Generate Menu from CSV """

    try:

        # Read CSS file
        with open(CSS_FILEPATH) as f:
            css = f.read()

        # Escape CSS
        css = escape(css)

        # Start HTML output
        html = """
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <script src="https://kit.fontawesome.com/a076d05399.js"></script>
                </head>
                <body>
                <style>
                    {}
                </style>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <div class="menu-body">
            """.format(
                css
            )

        # Read Request Data: CSV in bytes
        data = request.data
        restaurant_name = request.headers['restaurant_name']
        output_id = request.headers['output_id']

        # Restaurant name
        html += """
            <div>
                <h1> {} </h1>
            </div>
            """.format(restaurant_name)

        # Read file with Pandas
        df = pd.read_csv(io.BytesIO(data), encoding='utf8', sep=",")

        # Fill NA with empty values
        df = df.fillna('')

        # Extract Categories
        categories = df['category'].unique().tolist()
        categories = [ c for c in categories if not c == '']

        # Extract all records
        raw_items = df.to_dict(orient='records')

        # Category to Items dictionary
        category_to_items = defaultdict(list)

        # Only add item if at least it has category and name
        for item in raw_items:
            category = item['category']
            name = item['name']
            if not category == '' and not name == '':
                category_to_items[category].append(item)

        # Filter out those categories with no items
        for key, l in category_to_items.items():
            if not len(l) > 0:
                del category_to_items[key]

        # Track when categories and subcategories are added (not to repeat them)
        used_categories = set()
        used_subcategories = set()

        # from pprint import pprint
        # pprint(category_to_items)
        #
        for c, category in enumerate(category_to_items.keys()):

            # Items
            items = category_to_items[category]

            # Escape Category
            category = escape(category)

            for i, item in enumerate(items):

                # Name
                item_name = escape(item["name"])

                # Category
                item_category = escape(item["category"])

                # Subcategory
                item_subcategory = escape(item["subcategory"])

                # Valid category / subcategory
                valid_category = item_category != '' and item_name != ''
                valid_subcategory = item_subcategory != '' and item_name != ''

                # Menu Section
                if valid_category and category not in used_categories:

                    # Add Heading 2
                    html += """
                        <div class="menu-section">
                            <h2 class="menu-section-title"> {} </h2>
                        </div>
                        """.format(category)

                    used_categories.add(category)

                # Subcategory
                if valid_subcategory and item_subcategory not in used_subcategories:

                    # Add Heading 2
                    html += """
                        <div class="menu-section">
                            <h3 class="menu-subsection-title"> {} </h3>
                        </div>
                        """.format(item_subcategory)

                    used_subcategories.add(item_subcategory)

                # Add item
                if valid_category:

                    # # Special Title: Add Heading 2
                    # html += """
                    # <div>
                    #     <h2 class="menu-section-title-special"> {} </h2>
                    # </div>""".format(
                    #     item_category
                    # )

                    # Price
                    item_price = format_price(item["price"])

                    # Description
                    item_description = escape(item["description"])

                    # Suitable For
                    suitable = [
                        ( escape(item["vegetarian"]), "(V)" ),
                        ( escape(item["vegan"]), "(V+)" )
                    ]

                    # Add Suitable For
                    desc_suitable = [ addon[1] for addon in suitable if is_true(addon[0]) ]
                    suitable = ''
                    if len(desc_suitable):
                        suitable += ''.join(desc_suitable)

                    # Allergens
                    allergens = [
                        ( escape(item["allergy_gluten"]), "wheat" ),
                        ( escape(item["allergy_crustaceans"]), "crustacena" ),
                        ( escape(item["allergy_eggs"]), "eggs" ),
                        ( escape(item["allergy_fish"]), "fish" ),
                        ( escape(item["allergy_peanuts"]), "peanut" ),
                        ( escape(item["allergy_soybeans"]), "soya" ),
                        ( escape(item["allergy_milk"]), "milk" ),
                        ( escape(item["allergy_nuts"]), "treenut" ),
                        ( escape(item["allergy_celery"]), "celery" ),
                        ( escape(item["allergy_mustard"]), "mustard" ),
                        ( escape(item["allergy_sesame"]), "sesame" ),
                        ( escape(item["allergy_sulphites"]), "sulphurdioxide" ),
                        ( escape(item["allergy_lupin"]), "lupin" ),
                        ( escape(item["allergy_molluscs"]), "molluscs" ),
                    ]

                    # Add Allergens
                    bool_allergens = [ (is_true(x), y) for x,y in allergens ]

                    # Comments: to be added
                    item_comments = escape(item["comments"])

                    # Calories: to be formatted and added
                    item_calories = escape(item["calories"])

                    html += """
                        <div id="{}" class="menu-item">
                            <div class="menu-item-name">
                                <div class="arrow"><i class="fas fa-chevron-down"></i> {} {}</div>
                            </div>
                            <div class="menu-item-price"> {} </div>
                            <div>{}</div>
                            <div class="menu-item-description smalldesc">
                                <div>
                            """.format(
                                str(c) + str(i),
                                item_name,
                                suitable,
                                item_price,
                                item_description)

                    

                    if not item['comments'] == '':
                        html += """
                            <div><i>{}</i></div>
                        """.format(item['comments'])
                    
                    html += "<p><b>Nutrition Label:</b><p>"
                    
                    if not item['calories'] == '':
                        html += """
                            <div>{} kCal</div>
                        """.format(item['calories'])

                    for allergen in bool_allergens:
                        color = '_amber_' if allergen[0] else '_grey_'
                        html += """
                                    <img src="{}" class="icon" />
                                """.format(join(ICONS_FILEPATH, allergen[1], 'PNG', allergen[1] + color + '50x50.png'))

                    html += """
                                </div>
                            </div>
                        </div>
                        """

            # HTML thematic break
            html += "<hr>"

        html += addScript(category_to_items)

        # Footer
        html += """</div>
            <div class="footer">
                Menu made using <a href=https://godigital.menu target='_blank'>godigital.menu</a>
            </div>"""


        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Prettify it
        html = soup.prettify()

        # Write it!
        with open(os.path.join(OUTPUT_PATH, output_id) + '.html', "w") as html_file:
            html_file.write(html)

        # Hurray!
        return '200'

    except Exception as e:

        print('#' * 100)
        print('Exception', e)
        print('#' * 100)

        # Fail!
        return '500'


def is_true(value):
    """ Is this value True? """

    return value.lower() in [ 'yes', 'y', 'sí', 'si', 'oui' ]

def addScript(cat2ite):
    html = """
    <script>
        var items = [];
        var arrow_up = "\u25B4";
        var arrow_down = "\u25BE";
    """

    counter = -1
    for i, (k,v) in enumerate(cat2ite.items()):
        for j, ite in enumerate(v):
            counter += 1
            html += """
            items[{}] = document.getElementById('{}');
            items[{}].addEventListener('click', function() {{
                items[{}].querySelector('.smalldesc').classList.toggle('expand');
                items[{}].querySelector('.arrow').classList.toggle('up');
             }});
             """.format(counter, str(i)+str(j), counter, counter, counter)
    html += """
    </script>
    """
    return html

def format_price(value):
    """ Format price """

    # Convert to String first
    value = str(value).lower()

    # Extract numbers only
    # https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
    values = re.findall(r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", value)
    if len(values) == 0: return ''
    value = values[0]

    # Format it with 2 decimals
    value = '{:.2f}'.format(float(value)) if float(value) > 0 else ''

    # Remove '.00' if present
    value = value.rstrip('.00') if value.endswith('.00') else value

    # Escape when it is a String
    return escape(value)


# If run in localhost
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
