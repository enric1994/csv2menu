# imports
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


# Static path
STATIC_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"))
CSS_FILEPATH = join(STATIC_PATH, 'css', 'style.css')
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

    # Read CSS file
    with open(CSS_FILEPATH) as f:
        css = f.read()

    # Escape CSS
    css = escape(css)

    # Start HTML output
    # <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    # <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    html = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
            <title>GoDigital Menu</title>
            </head>
            <body>
            <style>
                {}
            </style>
            """.format(css)

    # Render HTML Modal Pop-up
    html += render_modal(restaurant_name)

    # Add meta tag and open body
    html += """
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <div class="menu-body">
        """
    
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

    # Don't display unavailable items
    for i, row in enumerate(df['available']):
        if not is_true(row):
            df = df.drop(i)

    # Extract Categories
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
        category = item['category']
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

    # Track when categories and subcategories are added (not to repeat them)
    used_categories = set()
    used_subcategories = set()

    # Move items with no category to the end
    desired_order_list = list(category_to_items.keys())
    if ' ' in desired_order_list:
        desired_order_list.remove(' ')
        desired_order_list.append(' ')
        category_to_items = {k: category_to_items[k] for k in desired_order_list}

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
                    """.format(category)

                used_categories.add(category)

            # Subcategory
            if valid_subcategory and item_subcategory not in used_subcategories:

                # Add Heading
                html += """
                    <div class="menu-section">
                        <h3 class="menu-subsection-title"> {} </h3>
                    </div>
                    """.format(item_subcategory)

                used_subcategories.add(item_subcategory)

            # Add item
            if valid_category:

                # Price
                item_price = format_price(item["price"])

                # Description
                item_description = escape(item["description"])

                # Suitable For
                item_suitable = format_suitable(item)

                # Comments: to be added
                item_comments = escape(item["comments"])
                item_comments = "Comments by owner: <i> {} </i>".format(item_comments) if item_comments else ''

                # Calories
                item_calories = format_calories(item["calories (kCal)"])

                # Allergens
                html_allergens = format_allergens(item)

                # Click here
                click_here = 'Tap on dish for nutritional information or comments' \
                    if item_comments or item_calories or html_allergens else ''

                # Label for Nutrition
                nutrition_label = 'Nutrition Label' if click_here else ''

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
                        <div class="smalldesc">
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
                        nutrition_label,
                        item_calories,
                        html_allergens,
                        # item_comments
                    )

        # HTML thematic break
        html += "<hr>"

    # Close menu-body
    html += "</div>"

    # Add function to expand item
    html += """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <script>

            function clickItem(x) {{
                x.querySelector('.smalldesc').classList.toggle('expand');
            }}

            function setCookie(cname, exhours) {{
                var d = new Date();
                d.setTime(d.getTime() + (exhours*60*60*1000));
                var expires = "expires="+ d.toUTCString();
                var cookiee = cname + "=" + "true" + "," + expires + ",path=/";
                document.cookie = cookiee;
            }}

            function getCookie(cname) {{
                var name = cname + "=";
                var ca = document.cookie.split(';');
                for(var i = 0; i < ca.length; i++) {{
                    var c = ca[i];
                    while (c.charAt(0) == ' ') {{
                      c = c.substring(1);
                    }}
                    if (c.indexOf(name) == 0) {{
                      return c.substring(name.length, c.length);
                    }}
                }}
                return "";
            }}

            function checkCookie() {{
                var cookie_modal = getCookie("modal");
                if (cookie_modal != "") {{
                    modal.style.display = "none";
                }} else {{
                  setCookie("modal", 1);
                }}
            }}

            // Tracking function
            function sendEmail(){{
                var input = document.getElementById("email").value;
                if (input.length > 0) {{
                    
                    // Hide modal
                    modal.style.display = "none";

                    // Add email to database
                    $.ajax({{
                        url: "https://api.godigital.menu/tracking",
                        type: "POST",
                        headers: {{
                            'Content-Type': 'text/plain',
                            'restaurantname': '{}',
                            'restaurantid': '{}',
                            'customeremail': input
                        }}
                    }});
                }}
            }}

            // Modal functions
            let modal = document.querySelector(".modal")
            let closeBtn = document.querySelector(".close-btn")

            closeBtn.onclick = function(){{
              modal.style.display = "none";
            }}

            window.onclick = function(e){{
              if(e.target == modal){{
                modal.style.display = "none";

              }}
            }}

            // Set cookie in order to avoid showing modal multiple times within same hour
            checkCookie();

        </script>
    """.format(restaurant_name, output_id)

    # Footer
    html += """
        <div class="footer">
            Menu made using <a href=https://godigital.menu target='_blank'>godigital.menu</a>
        </div>
    """

    # HTML ID (hidden)
    html += "<div style='color:white;'>Menu ID: {}</div>".format(output_id)

    # Closing body and html tags
    html += """ </body> </html> """

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Prettify it
    html = soup.prettify()

    # Write it!
    with open(os.path.join(OUTPUT_PATH, output_id) + '.html', "w") as html_file:
        html_file.write(html)


def render_modal(restaurant_name):
    """ Render Modal """
    
    return """
        <div class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <a href="#close" class="close-btn">&times;</a>
                    <div class="modal-header-text">WARNING</div>
                </div>
                <div class="modal-body">
                    <div class="modal-text">
                        In {} we want to help to you stay away from the COVID 19. Insert your email if you want to receive a warning in case someone infected attended our restaurant the same day. We will delete your data after incubation time!
                    </div>
                    <input type="text" id="email" placeholder="Your email..."><br><br>
                </div>
                <div class="modal-footer">
                    <div
                        class="modal-footer-text"
                        onClick="sendEmail()">
                            Add me to tracking list
                    </div>
                </div>
            </div>
        </div>

    """.format(restaurant_name)


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
        ( escape(item["allergy_gluten"]), "Gluten" ),
        ( escape(item["allergy_crustaceans"]), "Crustaceans" ),
        ( escape(item["allergy_eggs"]), "Eggs" ),
        ( escape(item["allergy_fish"]), "Fish" ),
        ( escape(item["allergy_peanuts"]), "Peanuts" ),
        ( escape(item["allergy_soybeans"]), "Soybeans" ),
        ( escape(item["allergy_milk"]), "Milk" ),
        ( escape(item["allergy_nuts"]), "Nuts" ),
        ( escape(item["allergy_celery"]), "Celery" ),
        ( escape(item["allergy_mustard"]), "Mustard" ),
        ( escape(item["allergy_sesame"]), "Sesame Seeds" ),
        ( escape(item["allergy_sulphites"]), "Sulphites" ),
        ( escape(item["allergy_lupin"]), "Lupin" ),
        ( escape(item["allergy_molluscs"]), "Molluscs" ),
    ]

    # Extract true values
    values = [ acronym for text, acronym in allergens if is_true(text) ]
    if len(values) == 0: return ''

    # Format output
    values_formatted = [
        "<span> {}: {} </span>".format(allergens_prefix[value], value) for value in values ]

    # Convert to string
    value = '<br>'.join(values_formatted)

    # Escape when it is a String
    return value

    # # HTML output
    # # Format output in two columns with Bootstrap
    # first_half = values[:len(values) // 2]
    # second_half = values[len(values) // 2:]
    # _html = """
    #     <div class="row">
    # """
    # for _list in [ first_half, second_half ]:
    #     _html += """
    #         <div class="col-md-6 col-sm-6 col-xs-6">
    #     """
    #     for value in _list:
    #         _html += """
    #             <div class="row">
    #                 <div class="col-md-2 col-sm-3 col-xs-3">
    #                     <p class="item-allergen-title">
    #                         {}
    #                     </p>
    #                 </div>
    #                 <div class="col-md-10 col-sm-9 col-xs-9">
    #                     <p class="item-allergen-description">
    #                         {}
    #                     </p>
    #                 </div>
    #             </div>
    #         """.format(
    #             allergens_prefix[value],
    #             value
    #         )
    #     _html += """
    #         </div>
    #     """
    # _html += """
    #     </div>
    # """
    # return _html
