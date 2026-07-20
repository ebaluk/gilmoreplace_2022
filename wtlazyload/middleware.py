import re


def imgsrcrepl(matchobj):    
    return '%s src="%s"' % (matchobj.group(1), matchobj.group(6)) if 'false' == matchobj.group(3) else '%s data-src="%s" data-lazyload="true"' % (matchobj.group(1), matchobj.group(6))  

def imgsrcrepl_bg(matchobj):    
    return '%s style="background-image: url(%s)"' % (matchobj.group(1), matchobj.group(6)) if 'false' == matchobj.group(3) else '%s data-src="%s" data-lazyload="true"' % (matchobj.group(1), matchobj.group(6))  

from django.utils.deprecation import MiddlewareMixin
class LazyLoadMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if not request.path.startswith("/admin"):            
            if response['Content-Type'].startswith('text/html'):            
                #s = re.sub(r'style="background-image:[\s]*url\(([^\)]+)\)"', r'data-src="\1" data-lazyload="true"', response.content.decode('utf-8'))
                s = re.sub(r'(<div([\s]+data-lazyload="(false|true)")?([\s]+(class|data-[0-9a-z\-_]+)="[^"]*")?)[^>]*style="background-image:[\s]*url\(([^\)]+)\)"', imgsrcrepl_bg, response.content.decode('utf-8'))
                response.content = re.sub(r'(<img([\s]+data-lazyload="(false|true)")?([\s]+(class|style|data-[0-9a-z\-_]+)="[^"]*")?)[^>]*src="([^\"]+)"', imgsrcrepl, s)
        return response

