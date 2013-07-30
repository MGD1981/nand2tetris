from sys import argv



def process_file(jack_file):
    pass

def process_directory(jack_directory):
    pass


if __name__ == '__main__':
    script, to_be_tokenized = argv

    if to_be_tokenized[-1] == '/':
        to_be_tokenized = to_be_tokenized[:-1]

    if '/' not in to_be_tokenized:
        slash_index = 0
    else:
        slash_index = to_be_tokenized.rfind('/')
    if '.' in to_be_tokenized[slash_index:]:
        if to_be_tokenized[-5:] == '.jack':
            process_file(to_be_tokenized)
        else:
            print "\nArgument must be .jack file or directory."
            raise NameError
    else:
        process_directory(to_be_tokenized)
