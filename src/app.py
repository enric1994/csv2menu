# imports
from flask import Flask, jsonify, request
from utils import render

# APP
app = Flask(__name__)


@app.route('/menu', methods=['GET', 'POST'])
def generate_menu():
    """ Generate Menu from CSV """

    # Read Request Data: CSV in bytes
    data = request.data
    restaurant_name = request.headers['restaurant_name']
    output_id = request.headers['output_id']
    
    # Render HTML
    render(data, restaurant_name, output_id)

    try:

        # Hurray!
        return '200'

    except Exception as e:

        print('#' * 100)
        print('Exception', e)
        print('#' * 100)

        # Fail!
        return '500'


# If run in localhost
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
