if f.values > 10:
    if a.name == f.name:  # todo: "text-multi"?
        if (not f.text_all and not any([x in f.match for x in a.value.split(",")])) \
                or \
                (f.text_all and not all([x in f.match for x in a.value.split(",")])):  # and
            w -= 1
            break
elif a.name == f.name and a.value not in f.match:  # or
    w -= 1
    break