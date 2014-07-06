# -*- encoding:utf-8 -*-
def dynamic_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def get_public_members(object):
    results = []
    for key in dir(object):
        if key.startswith("_"):
            continue
        try:
            value = getattr(object, key)
        except AttributeError:
            continue
        results.append((key, value))
    return results