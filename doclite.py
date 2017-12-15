import os

class Database(object):
    def __init__(self, filename, global_keyword):
        self.file_dir = filename + '/'
        self.global_keyword = global_keyword

    def __getitem__(self, key):
        for part in key:
            if '..' in part or '/' in part:
                return ''
        filename = self.file_dir + '/'.join(key)

        try:
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file = open(filename, 'r')
            value = file.read()
            file.close()
        except OSError:
            key = (self.global_keyword,) + key[1:]
            filename = self.file_dir + '/'.join(key)
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
        filename = self.file_dir + '/'.join(key)
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        file = open(filename, 'w')
        file.write(value)
        file.close()

    def __delitem__(self, key):
        filename = '/'.join(key)
        os.rmdir(self.file_dir + filename)

if __name__=='__main__':
    d = Database('.')
