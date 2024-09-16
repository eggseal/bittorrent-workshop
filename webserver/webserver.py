from flask import Flask, send_from_directory, abort
from os.path import join, dirname, abspath, exists

app = Flask(__name__)

# Define the folder where your files are stored
FILE_DIRECTORY = join(dirname(abspath(__file__)), "res")

@app.route('/files/<filename>')
def download_file(filename):
    # Construct the full file path
    file_path = join(FILE_DIRECTORY, filename)
    print(file_path)

    # Check if the file exists in the directory
    if exists(file_path):
        # Send the file from the directory
        return send_from_directory(FILE_DIRECTORY, filename, as_attachment=True)
    else:
        # Return a 404 error if the file does not exist
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
