import re

class ProfanityFilter:
    letter2regex = {
        'a': "[aA@]",
        'b': "([bB]|([iIl!1\\|]3))",
        'c': "[cC\\(kK]",
        'd': "([dD]|([iIl!1\\|]\\)))",
        'e': "[eE3]",
        'f': "(f|F|ph|Ph|pH|PH)",
        'g': "[gG6]",
        'h': "[hH]",
        'i': "[iIl!1\\|]",
        'j': "[jJ]",
        'k': "[cC\\(kK]",
        'l': "[Ll!1\\|]",
        'm': "[mM]",
        'n': "[nN]",
        'o': "[oO0]",
        'p': "[pP]",
        'q': "[qQ9]",
        'r': "[rR]",
        's': "[sS$5]",
        't': "[tT7]",
        'u': "[uUvV]",
        'v': "[vVuU]",
        'w': "([wW]|vv|vV|Vv|VV)",
        'x': "[xX]",
        'y': "[yY]",
        'z': "[zZ2]"
    }
    def __init__(self, client, *args, **kwargs):
        #super(ProfanityFilter, self).__init__(client, *args, **kwargs)
        filter_file = open(kwargs.get('filter_file', "db/bad_word_list"), 'r')
        replace_file = open(kwargs.get('replace_file', "db/bad_word_replace"), 'r')

        filter_list = ["heck"] # filter_file.read().split("\n")
        self.replace_list = replace_file.read().split("\n")

        self.regex_string = "\\b("

        for filter_word in filter_list:
            self.regex_string += "("
            for char in filter_word:
                self.regex_string += self.letter2regex[char]
            self.regex_string += ")|"

        self.regex_string = self.regex_string[:-1] +")\\b"
        print(self.regex_string)
        self.regex = re.compile(self.regex_string)

    def random_replace(self):
        return random.choice(self.replace_list)

    def filter(self, message):
        print(type(message))
        match = re.match(self.regex, message)
        print(message, match)
        return ""
