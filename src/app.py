# imports
import os
import io
import sys
import csv
import pandas as pd
from html import escape
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
from collections import defaultdict

# APP
app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is my secret key!'


# Static path
STATIC_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"))
CSS_FILEPATH = os.path.join(STATIC_PATH, 'css', 'style.css')
OUTPUT_HTML = "/data/outputs/menu.html"


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

        used_categories = []
        used_subcategories = []

        
        # Restaurant name
        html += """
            <div>
                <h1> {} </h1>
            </div>
            """.format(restaurant_name)

        for category in category_to_items.keys():

            # Items
            items = category_to_items[category]

            # Escape Category
            category = escape(category)

            for item in items:
                # Name
                item_name = escape(item["name"])

                # Category
                item_category = escape(item["category"])

                # Subcategory
                item_subcategory = escape(item["subcategory"])

                # Menu Section
                if item_category != '' and item_name != '' and category not in used_categories:

                    # Add Heading 2
                    html += """
                        <div class="menu-section">
                            <h2 class="menu-section-title"> {} </h2>
                        </div>
                        """.format(category)

                    used_categories.append(category)

                # Subcategory
                if item_subcategory != '' and item_name != '' and item_subcategory not in used_subcategories:

                    # Add Heading 2
                    html += """
                        <div class="menu-section">
                            <h3 class="menu-subsection-title"> {} </h3>
                        </div>
                        """.format(item_subcategory)

                    used_subcategories.append(item_subcategory)

                # Special Title
                if item_name == '' and item_category != '':

                    # Add Heading 2
                    html += """
                    <div>
                        <h2 class="menu-section-title-special"> {} </h2>
                    </div>""".format(
                        item_category
                    )

                if item_category != '' and item_name != '':

                    # Price
                    item_price = item["price"]
                    # Convert to float if it is a number
                    if item_price.replace('.','',1).isdigit():
                        item_price = '{:.2f}'.format(float(item_price)) if float(item_price) > 0 else ''
                    else:
                        item_price = ''
                    # Escape when it is a String
                    item_price = escape(item_price)

                    # Description
                    item_description = escape(item["description"])

                    # Addons
                    item_vegan = escape(item["vegan"])
                    item_glutenfree = escape(item["allergy_gluten"])

                    # Addons for Description
                    desc_addons = []
                    if is_true(item_vegan):
                        desc_addons.append("Vegan")
                    if is_true(item_glutenfree):
                        desc_addons.append("Gluten-Free")
                    if len(desc_addons):
                        item_description += " (" + ', '.join(desc_addons) + ")"

                    html += """
                        <div class="menu-item">
                            <div class="menu-item-name"> {} </div>
                            <div class="menu-item-price"> {} </div>
                            <div class="menu-item-description"> {} </div>
                        </div>
                        """.format(
                            item_name,
                            item_price,
                            item_description
                        )
            html += "<hr>"

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
        with open(OUTPUT_HTML, "w") as html_file:
            html_file.write(html)

        # Hurray!
        return jsonify(success=True)

    except Exception as e:

        print('#' * 100)
        print('Excepction', e)
        print('#' * 100)

        # Fail!
        return jsonify(success=False)


def is_true(value):
    """ Is this value True? """

    return value.lower() in [ 'yes', 'y', 'sí', 'si', 'oui']


# If run in localhost
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
