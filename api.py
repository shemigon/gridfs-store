import mimetypes
from bson.objectid import ObjectId
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


class File(object):
    def __init__(self, filename, content_type=None):
        self.filename = filename
        self.content_type = (content_type
                             or mimetypes.guess_type(filename)[0]
                             or 'application/octet-stream')

    def read(self):
        with open(self.filename, 'rb') as f:
            return f.read()


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


def current_user():
    '''
    In real application should be changed to something meaningful
    '''
    return 'test_user'


def url_for(user, oid):
    if storage(user).exists(ObjectId(oid)):
        pattern = USER_FILE_URLS.get(user, BASE_FILE_URL)
        return pattern % {'user': USER_ACCESS_KEYS[user], 'oid': oid}


def save_file(user, file):
    if file:
        content = file.read()
        fs = storage(user)
        with fs.new_file(filename=check_filename(file.filename),
                         content_type=file.content_type) as f:
            f.write(content)
        return unicode(f._id)


def oid_by_name(user, filename):
    fs = storage(user)
    if fs.exists(filename=filename):
        return unicode(fs.get_last_version(filename=filename)._id)
