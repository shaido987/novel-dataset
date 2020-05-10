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


def get_bool(string):
    """
    Convenience function to convert a string to a boolean.
    Handles Yes, yes, No and no.
    
    :param string: String to convert to boolean.
    :retruns: The boolean representation of the string or None.
    """
    if string is None:
        return None
    
    if string.lower() == "yes":
        return True
    elif string.lower() == "no":
        return False
    else:
        return None