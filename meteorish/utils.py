import random
import sockjs
import aiohttp


UNMISTAKABLE_CHARS = "23456789ABCDEFGHJKLMNPQRSTWXYZabcdefghijkmnopqrstuvwxyz"


def gen_id(chars=17):
    res = ""
    for i in range(chars):
        res += random.choice(UNMISTAKABLE_CHARS)
    return res


def _get_raw_request_from_stack(call_stack):
    # XXX Quick hack, there's no way to access headers via sockjs package
    # Maybe send a pull request or fork one
    for frame_info in call_stack:
        obj = frame_info.frame.f_locals.get("self")
        if (frame_info.function in ("client", "process") and
                isinstance(obj, sockjs.transports.base.Transport)):
            return obj.request


KEEP_HEADERS = ["REFERER", "X-CLIENT-IP", "X-FORWARDED-FOR",
                "X-CLUSTER-CLIENT-IP", "VIA", "X-REAL-IP", "HOST",
                "USER-AGENT", "ACCEPT-LANGUAGE"]


def _filter_headers(raw_headers):
    headers = raw_headers.copy()
    for key in raw_headers:
        if key not in KEEP_HEADERS:
            del headers[key]
    return aiohttp.multidict.CIMultiDictProxy(headers)
