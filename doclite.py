import os
import threading
import json
import logging as log

class Database(object):
    def __init__(self, filename, global_keyword):
        self.file_dir = str(filename) + '/'
        self.global_keyword = str(global_keyword)

    def __getitem__(self, key):
        for unparsed_part in key:
            part = str(unparsed_part)
            if '..' in part or '/' in part:
                return ''
        filename = os.path.join(self.file_dir, *map(str, key))

        try:
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file = open(filename, 'r')
            value = file.read()
            file.close()
        except OSError:
            key = (self.global_keyword,) + key[1:]
            filename = os.path.join(self.file_dir, *key)
            try:
                directory = os.path.dirname(filename)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                file = open(filename, 'r')
                value = file.read()
                file.close()
            except OSError:
                value = ''

        return value

    def __setitem__(self, key, value):
        for unparsed_part in key:
            part = str(unparsed_part)
            if '.' in part or '/' in part:
                return ''
        filename = os.path.join(self.file_dir, *map(str, key))
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        file = open(filename, 'w')
        file.write(value)
        file.close()

    def __delitem__(self, key):
        filename = os.path.join(self.file_dir, *key)
        os.rmdir(filename)

class InMemDatabase(Database):
    def __init__(self, *args, **kwargs):
        super(InMemDatabase, self).__init__(*args, **kwargs)
        self.dct = dict()
        self.copy_local_storage()

    def copy_local_storage(self):
        root = tuple()
        self._copy_local_storage_recur(root)

    def _copy_local_storage_recur(self, root):
        root_path = os.path.join(self.file_dir, *root)
        files = os.listdir(root_path)
        for filename in files:
            full_filename = os.path.join(root_path, filename)
            if os.path.isfile(full_filename):
                file = open(full_filename, 'r')
                self.dct[root+(filename,)] = file.read()
                file.close()
            if os.path.isdir(full_filename):
                self._copy_local_storage_recur(root+(filename,))

    def __setitem__(self, key, value):
        self.dct[key] = value

    def __getitem__(self, key):
        if key in self.dct:
            return self.dct[key]
        else:
            return self.dct.get((self.global_keyword,) + key[1:], '')

    def __delitem__(self, key):
        try:
            del self.dct[key]
        except KeyError:
            pass

    def commit(self):
        for path in self.dct:
            super().__setitem__(path, self.dct[path])

class JsonDatabase(Database):
    def __init__(self, filename):
        self.filename = filename
        self._data = dict()

        # Load existing data if available
        if os.path.isfile(self.filename):
            try:
                with open(self.filename, 'r') as fd:
                    self._data = json.load(fd)
            except json.JSONDecodeError as e:
                pass

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data.get(key, None)

    def __delitem__(self, key):
        try:
            del self._data[key]
        except KeyError:
            pass

    def commit(self):
        with open(self.filename, 'w') as fd:
            json.dump(self._data, fd)

if __name__=='__main__':
    d = Database('.')
