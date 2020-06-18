# imports
import os
import io
import sys
import csv
import pandas as pd
from html import escape
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup


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

        # Read file with Pandas
        df = pd.read_csv(io.BytesIO(data), encoding='utf8', sep=",")

        # Fill NA with empty values
        df = df.fillna('')

        # Extract Categories
        categories = df['item_category'].unique().tolist()

        # Extract all records
        raw_items = df.to_dict(orient='records')

        # Category to Items dictionary
        category_to_items = {}
        for item in raw_items:
            category = item["item_category"]
            category_to_items.setdefault(category, [])
            category_to_items[category].append(item)

        used_categories = []

        for category in categories:

            # Items
            items = category_to_items[category]

            # Escape Category
            category = escape(category)

            for item in items:

                # Name
                item_name = escape(item["item_name"])

                # Category
                item_category = escape(item["item_category"])

                # Restaurant Name
                if category == '':

                    # Add Heading
                    html += """
                        <div>
                            <h1> {} </h1>
                        </div>
                        """.format(item_name)

                # Menu Section
                if item_category != '' and item_name != '' and category not in used_categories:
                    
                    # Add Heading 2
                    html += """ 
                        <div class="menu-section"> 
                            <h2 class="menu-section-title"> {} </h2> 
                        </div> 
                        """.format(category)

                    used_categories.append(category)

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
                    item_price = escape(str(item["item_price"]))

                    # Description
                    item_description = escape(item["item_description"])
                    
                    # Addons for Description
                    desc_addons = []
                    if is_true(item["item_vegan"]):
                        desc_addons.append("Vegan")
                    if is_true(item["item_glutenfree"]):
                        desc_addons.append("Gluten-Free")
                    if len(desc_addons):
                        item_description += ', '.join(desc_addons)

                    html += """
                        <div class="menu-item">
                            <div class="menu-item-name"> {} </div>
                            <div class="menu-item-price"> {:.2f} </div>
                            <div class="menu-item-description"> {} </div>
                        </div>
                        """.format(
                            item_name,
                            float(item_price),
                            item_description
                        )

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

        print('Excepction', e)

        # Fail!
        return jsonify(success=False)


def is_true(value):
    """ Is this value True? """

    value.lower() in [ 'yes', 'y', 'sí', 'si' ]


# If run in localhost
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
