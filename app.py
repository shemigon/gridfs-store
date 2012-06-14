from bson.objectid import ObjectId
from flask import Flask, request, abort
from pymongo import Connection
import gridfs


BASE_FILE_URL = 'files/%(user)s/%(oid)s/'

# these urls are set by someone somewhere and hardly it's a dict
USER_FILE_URLS = {
    'test_user2': 'custom/%(user)s/%(oid)s/'
}


# there are some rules on generating these keys
USER_ACCESS_KEYS = {
    'test_user': '9da1f8e0aecc9d868bad115129706a77'
}


app = Flask(__name__)


def storage(user):
    '''
    get user's file storage
    '''
    return gridfs.GridFS(getattr(Connection(), user))


def check_filename(filename):
    # don't forget filename can contain dangerous paths
    return filename


def user_by_key(key):
    for user, saved_key in USER_ACCESS_KEYS.items():
        if saved_key == key:
            return user
    return None


def url_for(user, oid):
    pattern = USER_FILE_URLS.get(user, BASE_FILE_URL)
    return pattern % {'user': user, 'oid': oid}


@app.route('/file/<key>/')
def debug_upload_file(key):
    user = user_by_key(key)
    if not user:
        abort(404)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Hey %s! Upload a new file</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    ''' % user


@app.route('/file/<key>/', methods=['POST'])
def upload_file(key):
    user = user_by_key(key)
    if not user:
        abort(404)
    file = request.files['file']
    if file:
        content = file.read()
        fs = storage(user)
        with fs.new_file(filename=check_filename(file.filename),
                         content_type=file.content_type) as f:
            f.write(content)
        return unicode(f._id)


@app.route('/file/<key>/<filename>/')
def get_id_by_filename(key, filename):
    user = user_by_key(key)
    if not user:
        abort(404)
    fs = storage(user)
    if fs.exists(filename=filename):
        return unicode(fs.get_last_version(filename=filename)._id)
    abort(404)


@app.route('/link/<key>/<oid>/')
def link_to_file(key, oid):
    user = user_by_key(key)
    if not user:
        abort(404)
    fs = storage(user)
    if fs.exists(ObjectId(oid)):
        return url_for(user, oid)
    abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
