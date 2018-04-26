import re
import random

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
        's': "[sS\\$5]",
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
        self.reset_filter()

    def reset_filter(self):
        filter_file = open("filter/bad_word_list", 'r')
        replace_file = open("filter/bad_word_replace", 'r')

        filter_list = filter_file.read().split("\n")
        self.replace_list = replace_file.read().split("\n")

        self.regex_string = "\\b("

        for filter_word in filter_list:
            if filter_word:
                self.regex_string += "("
                self.regex_string += "".join(map(
                    lambda char: self.letter2regex.get(char, "\\"+char),
                    filter_word
                ))  # Use "\\s*" to detect spaces in between letters as well
                self.regex_string += ")|"

        self.regex_string = self.regex_string[:-1] +")\\b"
        self.regex = re.compile(self.regex_string)

    def random_replace(self, *args):
        return random.choice(self.replace_list)

    def filter(self, message):
        filtered, num_subs = re.subn(self.regex, self.random_replace, message)
        if num_subs:
            return filtered
        else:
            return False
