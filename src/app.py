import io
import sys
import csv

import pandas as pd
from html import escape
from flask import Flask, jsonify, request
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/menu', methods=['GET', 'POST'])
def generate_menu():
    try:
        css = open('./style.css').read()

        data = request.data
        df = pd.read_csv(io.BytesIO(data), encoding='utf8', sep=",")
        df = df.fillna('')
        categories = list(set(df['item_category'].to_list()))
        rawItems = []
        for index, row in df.iterrows():
            rawItems.append(row.to_dict())

        category_list = dict()
        for category in categories:
            categoryItems = []
            for item in rawItems:
                itemCategory = item["item_category"]
                if category == itemCategory:
                    categoryItems.append(item)
            category_list[category] = categoryItems

        css = escape(css)

        html = "<style>" + css + "</style>"
        html += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
        html += "<div class=\"menu-body\">"

        used_categories = []

        for category in categories:
            print(category)
            items = category_list[category]
            category = escape(category)

            for item in items:
                print(item)
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
                    item["item_price"] = escape(str(item["item_price"]))

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

        html_file = open("/data/src/test_menu.html", "w")
        html_file.write(html)
        html_file.close()

        resp = jsonify(success=True)
        return resp
    except Exception as e:
        print('Excepction', e)
        resp = jsonify(success=False)
        return resp


app.run(host='0.0.0.0', port=5000, debug=True)
