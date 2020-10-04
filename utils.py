import sys


def get_value(element, check=lambda e: e.string, parse=lambda e: e.string.strip()):
    """
    Gets the value of a HTML element/node following the parse function. 
    This function is necessary since the novel pages are not always consistent with each other. 
    Also checks if the value is 'N/A' and returns None in that case.
    
    :param element: A HTML element/node.
    :param check: A function to be applied on the element. 
                  Checks if the element object have a retrun value for the function or is it's None.
    :param parse: A function to parse the element if it passes the check.
    :returns: The value returned by running the parse function on the element.
              None is returned if the element does not pass the check function or if the value is 'N/A'.
    """
    if check(element) is None:
        return None
    pe = parse(element)
    if ''.join(pe) == 'N/A':
        return None
    return pe

              
def get_value_str_txt(element, check_one=lambda e: e.string, parse_one=lambda e: e.string.strip(),
                      check_two=lambda e: e.text, parse_two=lambda e: e.text.strip()):
    """
    Used when it's unknown which function to apply on an element to obtain it's value.
    For example, if .string or .text should be used.
    The functions are applied in order, if the first one returns None then the second one is tried.
    
    :param element: A HTML element/node.
    :param check_one: A function to be applied on the element.
                      Checks if the element object have a retrun value for the function or is it's None.
    :param parse_one: A function to parse the element if it passes the check.
    :param check_two: A function to be applied on the element.
                      Checks if the element object have a retrun value for the function or is it's None.
    :param parse_two: A function to parse the element if it passes the check.
    :returns: The value returned by running parse_one or parse_two on the element.
    """
    res_one = get_value(element, check_one, parse_one)
    res_two = get_value(element, check_two, parse_two)
    return res_one or res_two
              

def is_empty(element):
    """
    Checks if running .string on the element returns an empty string.
    
    :param element: A HTML element/node.
    :returns: A boolean representing whether the element contains an empty string.
    """
    return get_value(element) == ""


def str2bool(argument):
    """
    Helper function to process input arguments of boolean type.

    :param argument: str
    :return: boolean
    """
    if argument is None:
        return None

    if argument.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif argument.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return None


def progressbar(it, prefix="", size=60):
    """
    Adds an progress bar when scraping.
    :param it: iterable, the list or iterable to run over.
    :param prefix: str, any prefix to use.
    :param size: int, the total length of the bar.
    """
    count = len(it)

    def show(j, novel_id):
        x = int(size*j/count)
        sys.stdout.write("\r%s[%s%s] %i/%i (current novel id: %s)" % (prefix, "#"*x, "."*(size-x), j, count, novel_id))
        sys.stdout.flush()

    sys.stdout.write("\r%s[%s] 0/%i" % (prefix, "."*size, count))
    for i, item in enumerate(it):
        yield item
        show(i+1, item)
    sys.stdout.write("\n")
    sys.stdout.flush()
