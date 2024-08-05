# -*- coding: utf-8 -*-
#
# Author: HolgerCremer@gmail.com
#

import json

from MoinMoin import user
from MoinMoin import log

logger = log.getLogger(__name__)

def execute(pagename, request):
    if request.method != "POST":
        request.write("Only json data with post is supported.")
        return

    try:
        token = request.cfg.auth_service_token
    except AttributeError:
        request.status_code = 403
        request.write("No auth configured")
        return

    try:
        auth = request.environ.get('HTTP_AUTH_TOKEN')
        if auth is None or auth != token:
            logger.info("Invalid auth (missing HTTP_AUTH_TOKEN")
            request.status_code = 403
            request.write("Invalid auth")
            return
        
        do = request.values.get('do')
        if do == "list":
            _list_user(request)
            return
        elif do == "loginCheck":
            _login_check(request)
            return
        elif do == "isInGroup":
            _is_in_group(request)
            return
    except Exception as e:
        logger.error("the error: %s" % e, e)


def _send_json(request, data_to_send):
    """
    Set the json content type and serialize the data to json
    :param request:
    :param data_to_send:
    """
    request.headers['Content-Type'] = 'application/json"'
    request.write(json.dumps(data_to_send))


def _list_user(request):
    user_list = []
    for uid in user.getUserList(request):
        # email, disabled, name, id,
        u = user.User(request, uid)
        if u.disabled:
            continue
        # groups_with_member
        user_list.append({
            "login": u.name,
            "email": u.email
        })

    _send_json(request, user_list)


def _login_check(request):
    """
    result values:
    'ok', 'wrong_password', 'unknown_user'

    Outputs json like
        {"result": "ok", "groups": []}
    or
        {"result": "wrong_password"}
    :param request:
    """
    data = json.loads(request.stream.read())
    u = user.User(request, None, data["login"], password=data["password"])
    if u.valid == 1:
        result = 'ok'
    elif u.exists():
        result = "wrong_password"
    else:
        result = "unknown_user"

    result_json = {
        "result": result
    }
    if u.valid and data.get("listGroups"):
        groups = list(request.groups.groups_with_member(u.name))
        result_json["groups"] = groups
    
    logger.info("Checking for user %s: %s" % (data["login"], result_json))
    _send_json(request, result_json)


def _is_in_group(request):
    """

    :param request:
    """
    data = json.loads(request.stream.read())
    logger.debug("Is user %s in group %s" % (data["login"], data["group"]))
    group = request.groups.get(data["group"])
    in_group = False
    if group is not None:
        in_group = data["login"] in group

    _send_json(request, {
        "inGroup": in_group
    })
