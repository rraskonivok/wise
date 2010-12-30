from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.utils.html import strip_spaces_between_tags as short

try:
    from sentry.client.models import sentry_exception_handler
    has_sentry = True
except:
    has_sentry = False


class XHTMLMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = short(response.content)
            # Mixed MathML + HTML contents needs this content
            # type otherwise Firefox won't render the MathML
            if hasattr(response,'xhtml') or settings.FORCE_XHTML:
                response["Content-Type"] = "application/xhtml+xml; charset=utf-8"
        return response


if has_sentry:
    class ErrorMiddleware(object):
        def process_exception(self, request, exception):
            # Make sure the exception signal is fired for Sentry

            if has_sentry:
                sentry_exception_handler(request=request)

            return exception
else:
    class ErrorMiddleware(object):
        pass

class BlockedIpMiddleware(object):
    def process_request(self, request):
        if request.META['REMOTE_ADDR'] in settings.BLOCKED_IPS:
            return HttpResponseForbidden('<h1>Your IP address has been reported for abuse.</h1>')
        return None
