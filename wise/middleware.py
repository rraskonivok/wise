from django.conf import settings
from django.utils.html import strip_spaces_between_tags as short
 
class XHTMLMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = short(response.content)
            # Mixed MathML + HTML contents needs this content
            # type otherwise Firefox won't render the MathML
            if hasattr(response,'xhtml') or settings.FORCE_XHTML:
                response["Content-Type"] = "application/xhtml+xml; charset=utf-8"
        return response
