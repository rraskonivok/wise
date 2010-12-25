from django.http import HttpResponse
from django.conf import settings
from django.utils.html import strip_spaces_between_tags as short
from sentry.client.models import sentry_exception_handler

class XHTMLMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = short(response.content)
            # Mixed MathML + HTML contents needs this content
            # type otherwise Firefox won't render the MathML
            if hasattr(response,'xhtml') or settings.FORCE_XHTML:
                response["Content-Type"] = "application/xhtml+xml; charset=utf-8"
        return response

class ErrorMiddleware(object):
    def process_exception(self, request, exception):
        # Make sure the exception signal is fired for Sentry
        sentry_exception_handler(request=request)
        return HttpResponse('500')
