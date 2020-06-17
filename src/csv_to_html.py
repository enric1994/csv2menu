# Credit: https://github.com/dasmer/piatto

import sys
import csv
import io
from html import escape
from IPython import embed
from bs4 import BeautifulSoup

def render(csv_path, sheet_link):
    try:
        css = open('./style.css').read()
        my_csv = csv.DictReader(io.open(csv_path, "r", encoding = "utf-8-sig"))

        categories = []
        rawItems = []
        for item in my_csv:
            rawItems.append(item)
            category = item["item_category"]
            if category not in categories:
                categories.append(category)


        category_list = dict()
        for category in categories:
            categoryItems = []
            for item in rawItems:
                itemCategory = item["item_category"]
                if category == itemCategory:
                    categoryItems.append(item)
            category_list[category] = categoryItems

        css = escape(css)
        embed()
        html = "<style>" + css + "</style>"
        html += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
        html += "<div class=\"menu-body\">"

        used_categories = []

        for category in categories:

            items = category_list[category]
            category = escape(category)

            for item in items:
                # Normal title (name and category)
                if item["item_category"] != '' and item["item_name"] != '' and category not in used_categories:
                    html+= "<div class=\"menu-section\"><h2 class=\"menu-section-title\">" + category + "</h2></div>"
                    used_categories.append(category)

                if item["item_category"] != '' and item["item_name"] != '':
                    description = item["item_description"]
                    if item["item_vegan"] == "YES":
                        description += "(Vegan)"
                    if item["item_glutenfree"] == "YES":
                        description += "(Gluten-Free)"

                    description = escape(description)
                    item["item_name"] = escape(item["item_name"])
                    item["item_price"] = escape(item["item_price"])

                    html += "<div class=\"menu-item\">"

                    html += "<div class=\"menu-item-name\">" + item["item_name"] + "</div>"

                    if item["item_price"] == '0':
                        html += "<div class=\"menu-item-price\"> </div>"
                    else:
                        html += "<div class=\"menu-item-price\">" + '%.2f' % float(item["item_price"]) + "</div>"

                    html += "<div class=\"menu-item-description\">" + description + "</div>"

                    html += "</div>"

            # Restaurant name (only name)
            if item["item_category"] == '':
                html+= "<div><h1>" + item["item_name"] + "</h1></div>"

            # Special title (only category)
            if item["item_name"] == '' and item["item_category"] != '':
                html+= "<div><h2 class=\"menu-section-title-special\">" + item["item_category"] + "</h2></div>"



        html += "</div>"
        html += "<div class='footer'>Menu made using <a href=https://godigital.menu target='_blank'>godigital.menu</a></div>"

        soup = BeautifulSoup(html, "html.parser")

        html = soup.prettify()

        html_file = open("/data/src/{}.html".format(sheet_link), "w")
        html_file.write(html)
        html_file.close()
        return True
    except Exception as e:
        print(e)
        return False
render('./GoDigital Menu Example - GoDigital Menu (1).csv', 'example')
