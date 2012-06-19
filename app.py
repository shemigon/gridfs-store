import api
from flask import Flask, request, abort


app = Flask(__name__)


@app.route('/file/<key>/')
def debug_upload_file(key):
    user = api.user_by_key(key)
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
    user = api.user_by_key(key)
    if not user:
        abort(404)
    return api.save_file(user, request.files['file'])


@app.route('/file/<key>/<filename>/')
def get_id_by_filename(key, filename):
    user = api.user_by_key(key)
    if not user:
        abort(404)
    oid = api.oid_by_name(user, filename)
    if oid:
        return oid
    abort(404)


@app.route('/link/<key>/<oid>/')
def link_to_file(key, oid):
    user = api.user_by_key(key)
    if not user:
        abort(404)
    url = api.url_for(user, oid)
    if url:
        return url
    abort(404)


def sample_save_from_filesystem(filename):
    user = api.current_user()
    if user:
        try:
            fileHandle = api.File(filename)
            oid = api.save_file(user, fileHandle)
            return api.url_for(user, oid)
        except IOError:
            pass
    return ''


def sample_get_file_url(filename):
    user = api.current_user()
    if user:
        oid = api.oid_by_name(user, filename)
        if oid:
            return api.url_for(user, oid)
    return ''


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'file':
            filename = 'README'
            url = sample_save_from_filesystem(filename)
            print(u'%s = %s' % (filename, url))
        elif sys.argv[1] == 'url':
            filename = 'README'
            url = sample_get_file_url(filename)
            print(u'%s = %s' % (filename, url))
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
