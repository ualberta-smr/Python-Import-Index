from flask import Flask, json, make_response, render_template
from utils import get_db_connection
import markdown

app = Flask(__name__, template_folder='.')


@app.route('/')
def hello_world():  # put application's code here
    f = open('README.md', 'r')
    markdownFile = f.read()
    stringOfMarkdown = markdown.markdown(markdownFile, extensions=['markdown.extensions.toc', 'markdown.extensions.attr_list','markdown.extensions.codehilite','markdown.extensions.fenced_code'])
    return render_template('index.html', stringOfMarkdown = stringOfMarkdown)

# http://127.0.0.1:5000/library/discord.py:0.11.0,setuptools
@app.route('/library/<string:packages>')
def package_to_import(packages):
    conn = get_db_connection()
    cursor = conn.cursor()

    packages_json_list = {"result": [], "error": []}
    for package in packages.split(','):
        package = package.split(':')
        package_name = package[0]
        package_version = ""

        cursor.execute('SELECT * FROM packages WHERE package = %s', (package_name,))
        does_the_table_contain_this_package = cursor.fetchone()
        if does_the_table_contain_this_package is None:
            packages_json_list["error"].append(
                package_name + " OptionalVersion(" + package_version + ") isn't include in the dataset")
        else:
            if len(package) > 1:
                package_version = package[1]
                cursor.execute('SELECT * FROM import_names WHERE package_name = %s AND version = %s',
                               (package_name, package_version,))
                found_package = cursor.fetchall()
            else:
                cursor.execute('SELECT * FROM import_names WHERE package_name = %s', (package_name,))
                found_package = cursor.fetchall()
            packages_json_list["result"].extend(
                [{"library": i[2], "release": i[3], "import_name": i[1]} for i in found_package])
    conn.close()

    response = app.response_class(
        response=json.dumps(packages_json_list),
        mimetype='application/json'
    )
    return response


# http://127.0.0.1:5000/importname/discord,pkg_resources
@app.route('/importname/<string:imports>')
def import_to_package(imports):
    conn = get_db_connection()
    cursor = conn.cursor()

    imports_json_list = {"result": [], "error": []}
    for import_name in imports.split(','):
        if ':' in import_name:
            imports_json_list["error"].append(
                "The import name provided: " + import_name + " contains a ':' which is invalid")
            continue

        cursor.execute('SELECT * FROM import_names WHERE import_name = %s', (import_name,))
        does_the_table_contain_this_import = cursor.fetchall()
        if does_the_table_contain_this_import is None:
            imports_json_list["error"].append(
                "The import name provided: " + import_name + " isn't contained in our database")
        else:
            imports_json_list["result"].extend([{"library": i[2], "release": i[3], "import_name": i[1]} for i in
                                                does_the_table_contain_this_import])
    conn.close()

    response = app.response_class(
        response=json.dumps(imports_json_list),
        mimetype='application/json'
    )
    return response


@app.route('/dump')
def dump():
    with open('dump.csv', 'r') as fp:
        dump_of_database = fp.read()

    output = make_response(dump_of_database)
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
