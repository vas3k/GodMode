# -*- encoding:utf-8 -*-


def magic_params(request, key, value):
    params = dict([(k, v) for k, v in request.args.items()])
    if value:
        params.update({key: value})
    else:
        if key in params.keys():
            del params[key]

    if params:
        return "%s?" % request.path + "&".join(["%s=%s" % (k, v) for k, v in params.items()])
    else:
        return "%s" % request.path
