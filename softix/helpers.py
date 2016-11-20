def remove_none(data):
    if not data:
        return
    for k, v in data.items():
        if v is None:
            del(data[k])
