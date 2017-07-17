def __check_dict(data, search):
    """
    search dict for value
    :param data: dict
    :param search: search string value
    """
    return len(
        [x for x in data.values() if type(x) == str and search in x]) > 0


def json_contains(response, search):
    """
    search json response for value
    :param response: django response
    :param search: search string value
    """
    result = False
    data = response.json()
    if 'results' in data:
        data = data['results']
    if type(data) == list:
        for entry in data:
            result = __check_dict(entry, search)
            if result:
                break
    else:
        result = __check_dict(data, search)
    assert result
