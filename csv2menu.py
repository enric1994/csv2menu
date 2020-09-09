import os
from os.path import join, abspath, dirname
import pandas as pd
import re
from html import escape
from bs4 import BeautifulSoup
from collections import defaultdict
import io
import sys
import csv


CSS_FILEPATH = 'style.css'

OUTPUT_PATH = "/output/"

# Allergens prefix
allergens_prefix = {
    "Gluten": 'G',
    "Crustaceans": 'C',
    "Eggs": 'E',
    "Fish": 'F',
    "Peanuts": 'P',
    "Soybeans": 'S',
    "Milk": 'MK',
    "Nuts": 'N',
    "Celery": 'CY',
    "Mustard": 'MD',
    "Sesame Seeds": 'SS',
    "Sulphites": 'SP',
    "Lupin": 'L',
    "Molluscs": 'M',
}


def render(data, restaurant_name, output_id):
    """ Render HTML """

    # Escape restaurant name
    restaurant_name = escape(restaurant_name)

    # Read CSS file
    with open(CSS_FILEPATH) as f:
        css = f.read()

    # Escape CSS
    css = escape(css)

    # Start HTML output
    # <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    # <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    # <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    html = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
            <link rel="shortcut icon" href="https://img.icons8.com/wired/64/000000/restaurant-menu.png">
            <title>{}</title>
            </head>
            <body>
            <style>
                {}
            </style>
            """.format(restaurant_name, css)

    # Add meta tag and open body
    html += """
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <div class="menu-body">
        """

    # Restaurant name
    html += """
        <div>
            <h1> {} </h1>
        </div>
        """.format(restaurant_name)

    # Read file with Pandas
    df = pd.read_csv(data)

    # Fill NA with empty values
    df = df.fillna('')

    # Don't display unavailable items
    for i, row in enumerate(df['available']):
        if not is_true(row):
            df = df.drop(i)

    # Extract Categories
    df['category'] = df['category'].str.lower()
    df['subcategory'] = df['subcategory'].str.lower()
    categories = df['category'].unique().tolist()
    categories = [ c for c in categories if not c == '']

    # Define category for items with no category
    categories.append(' ')

    # Extract all records
    raw_items = df.to_dict(orient='records')

    # Category to Items dictionary
    category_to_items = defaultdict(list)

    # Only add item if at least it has category and name
    for item in raw_items:
        category = item['category'].lower()
        name = item['name']
        # If no category but has name (and is available), add it to orphan category ' '
        if category == '' and not name == '' and is_true(escape(item["available"])):
            category = ' '
            item['category'] = ' '
        if not category == '' and not name == '':
            category_to_items[category].append(item)

    # Filter out those categories with no items
    for key, l in category_to_items.items():
        if not len(l) > 0:
            del category_to_items[key]

    # Track when categories are added (not to repeat them)
    used_categories = set()

    # Move items with no category to the end
    desired_order_list = list(category_to_items.keys())
    if ' ' in desired_order_list:
        desired_order_list.remove(' ')
        desired_order_list.append(' ')
        category_to_items = {k: category_to_items[k] for k in desired_order_list}

    for category in category_to_items.keys():

        # Track when subcategories  are added (not to repeat them)
        used_subcategories = set()

        # Items
        items = category_to_items[category]

        for item in items:

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

                # Add Heading
                html += """
                    <div class="menu-section">
                        <h2 class="menu-section-title"> {} </h2>
                    </div>
                    """.format(format_euro(escape(' '.join([x.capitalize() for x in category.split(' ')]))))

                used_categories.add(category)

            # Subcategory
            if valid_subcategory and item_subcategory not in used_subcategories:

                # Add Heading
                html += """
                    <div class="menu-section">
                        <h3 class="menu-subsection-title"> {} </h3>
                    </div>
                    """.format(format_euro(escape(' '.join([x.capitalize() for x in item_subcategory.split(' ')]))))

                used_subcategories.add(item_subcategory)

            # Add item
            if valid_category:

                # Price
                item_price = format_euro(format_price(item["price"]))

                # Description
                item_description = format_euro(escape(item["description"]))

                # Suitable For
                item_suitable = format_suitable(item)

                # Comments: to be added
                item_comments = format_euro(escape(item["comments"]))
                item_comments = "<i> {} </i>".format(item_comments) if item_comments else ''

                # Calories
                item_calories = format_calories(item["calories (kCal)"])

                # Allergens
                html_allergens = format_allergens(item)

                # Click here
                click_here = 'Tap on dish for nutritional information' \
                    if item_comments or item_calories or html_allergens else ''

                # Label for Nutrition
                nutrition_label = 'Nutrition Label:' if click_here else ''

                # Add item
                html += """
                    <div class="menu-item" onclick="clickItem(this)">
                        <div class="menu-item-name">
                            {} {}
                        </div>
                        <div class="menu-item-price">
                            {}
                        </div>
                        <div class="menu-item-description">
                            {}
                        </div>
                        <small class="menu-click-label">
                            {}
                        </small>
                        <div class="collapsible">
                            <div class="menu-item-comments">
                                <i> {} </i>
                            </div>
                            <small class="menu-nutrional-label">
                                {}
                            </small>
                            <div class="menu-item-calories">
                                {}
                            </div>
                            <div class="menu-item-allergens">
                                {}
                            </div>

                        </div>
                    </div>
                    """.format(
                        item_name,
                        item_suitable,
                        item_price,
                        item_description,
                        click_here,
                        item_comments,
                        nutrition_label,
                        item_calories,
                        html_allergens
                    )

        # HTML thematic break
        html += "<hr>"

    # Close menu-body
    html += "</div>"

    # Add Javascript code
    html += add_js_code(restaurant_name, output_id)

    # HTML ID (hidden)
    html += "<div style='color:white;'>Menu ID: {}</div>".format(output_id)

    # Closing body and html tags
    html += """ </body> </html> """

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Prettify it
    html = soup.prettify()

    # Format euro in the whole HTML
    html = format_euro(html)

    # Write it!
    with open(output_id, "w") as html_file:
        html_file.write(html)

def is_true(value):
    """ Is this value True? """

    return value.lower() in [ 'yes', 'y', 'sí', 'si', 'oui' ]


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

    # Escape when it is a String
    return escape(value)


def format_calories(value):
    """ Format calories """

    # Convert to String first
    value = str(value).lower()

    # Extract numbers only
    values = re.findall(r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", value)
    if len(values) == 0: return ''
    value = values[0]

    # Format it with no decimals
    value = '{:.0f} kCal'.format(float(value)) if float(value) > 0 else ''

    # Escape when it is a String
    return escape(value)


def format_suitable(item):
    """ Format suitable """

    # Read inputs
    suitable = [
        ( escape(item["vegetarian"]), "V" ),
        ( escape(item["vegan"]), "Ve" )
    ]

    # Extract true values
    values = [ acronym for text, acronym in suitable if is_true(text) ]
    if len(values) == 0: return ''

    # Format output
    value = '(' + ', '.join(values) + ')'

    # Escape when it is a String
    return escape(value)


def format_allergens(item):
    """ Format allergens """

    allergens = [
        ( escape(item["allergen_gluten"]), "Gluten" ),
        ( escape(item["allergen_crustaceans"]), "Crustaceans" ),
        ( escape(item["allergen_eggs"]), "Eggs" ),
        ( escape(item["allergen_fish"]), "Fish" ),
        ( escape(item["allergen_peanuts"]), "Peanuts" ),
        ( escape(item["allergen_soybeans"]), "Soybeans" ),
        ( escape(item["allergen_milk"]), "Milk" ),
        ( escape(item["allergen_nuts"]), "Nuts" ),
        ( escape(item["allergen_celery"]), "Celery" ),
        ( escape(item["allergen_mustard"]), "Mustard" ),
        ( escape(item["allergen_sesame"]), "Sesame Seeds" ),
        ( escape(item["allergen_sulphites"]), "Sulphites" ),
        ( escape(item["allergen_lupin"]), "Lupin" ),
        ( escape(item["allergen_molluscs"]), "Molluscs" ),
    ]

    # Extract true values
    values = [ acronym for text, acronym in allergens if is_true(text) ]
    if len(values) == 0: return ''

    # Format output
    values_formatted = [
        "<span> <strong>{}:</strong> {} </span>".format(allergens_prefix[value], value) for value in values ]

    # Convert to string
    value = '<br>'.join(values_formatted)

    # Escape when it is a String
    return value


def format_euro(value):
    """ Format euro """

    # Replace € for html rendering
    value = value.replace('€', '&euro;')

    return value


def add_js_code(restaurant_name, output_id):
    """ Javascript code """

    return """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.3/js/intlTelInput.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.3/css/intlTelInput.min.css">
        <script>

            function clickItem(x) {{
                x.querySelector('.collapsible').classList.toggle('expand');
            }}

            

        </script>
    """.format(restaurant_name, output_id)

if __name__ == "__main__":
    print('Creating menu...')
    print('Input CSV path: ',sys.argv[1])
    print('Output HTML path: ',sys.argv[3])
    print('Restaurant Name: ',sys.argv[2])

    render(sys.argv[1], sys.argv[2], sys.argv[3])
