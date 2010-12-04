from django.utils.html import strip_spaces_between_tags as short
 
class XHTMLMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = short(response.content)
            response["Content-Type"] = "application/xhtml+xml; charset=utf-8"
        return response
