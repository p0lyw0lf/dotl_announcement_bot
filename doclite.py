import os
import threading

class Database(object):
    def __init__(self, filename, global_keyword):
        self.file_dir = filename + '/'
        self.global_keyword = global_keyword

    def __getitem__(self, key):
        for part in key:
            if '..' in part or '/' in part:
                return ''
        filename = os.path.join(self.file_dir, *key)

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
        for part in key:
            if '.' in part or '/' in part:
                return ''
        filename = os.path.join(self.file_dir, *key)
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

if __name__=='__main__':
    d = Database('.')
