# This file should contain a function called get_color_code().
# This function should take one argument, a color name,
# and it should return one argument, the hex code of the color,
# if that color exists in our data. If it does not exist, you should
# raise and handle an error that helps both you as a developer,
# for example by logging the request and error, and the user,
# letting them know that their color doesn't exist.
import json

def get_color_code(color_name):
    # this is where you should add your logic to check the color.
    # Open the file at data/css-color-names.json, and return the hex code
    # The file can be considered as JSON format, or as a Python dictionary.
    
    hex_code=[]

    with open('/Users/TiaSola/Desktop/CODE/SE/foundations/week1/foundations-sample-website/color_check/data/css-color-names.json') as json_file:
        data = json.load(json_file)
        if color_name in data:
            capitalized_color_name = color_name.capitalize()
            hex_code.append(capitalized_color_name)
            hex_code.append(data[color_name])
        elif color_name.strip() == "":
            hex_code.append("A color must be inserted")
        elif color_name not in data:
            hex_code.append("Color inserted doesn't exist")
        elif color_name.isnumeric():
            hex_code.append("Numbers are not allowed")
    return hex_code