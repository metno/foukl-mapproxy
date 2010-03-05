"""
Service exception handling (WMS exceptions, XML, in_image, etc.).
"""
from jinja2 import Environment, PackageLoader
from mapproxy.core.exceptions import ExceptionHandler, XMLExceptionHandler
from mapproxy.core.response import Response
from mapproxy.core.image import message_image

_env = Environment(loader=PackageLoader('mapproxy.wms', 'templates'),
                  trim_blocks=True)

class WMSXMLExceptionHandler(XMLExceptionHandler):
    env = _env

class WMS100ExceptionHandler(WMSXMLExceptionHandler):
    """
    Exception handler for OGC WMS 1.0.0 ServiceExceptionReports
    """
    template_file = 'wms100exception.xml'
    content_type = 'text/xml'

class WMS111ExceptionHandler(WMSXMLExceptionHandler):
    """
    Exception handler for OGC WMS 1.1.1 ServiceExceptionReports
    """
    template_file = 'wms111exception.xml'
    mimetype = 'application/vnd.ogc.se_xml'

class WMS130ExceptionHandler(WMSXMLExceptionHandler):
    """
    Exception handler for OGC WMS 1.3.0 ServiceExceptionReports
    """
    template_file = 'wms130exception.xml'
    mimetype = 'text/xml'

class WMSImageExceptionHandler(ExceptionHandler):
    """
    Exception handler for image exceptions.
    """
    def render(self, request_error):
        request = request_error.request
        params = request.params
        format = params.format
        size = params.size
        if size is None:
            size = (256, 256)
        transparent = ('transparent' in params
                       and params['transparent'].lower() == 'true')
        bgcolor = WMSImageExceptionHandler._bgcolor(request.params)
        result = message_image(request_error.message, size=size, format=format,
                               bgcolor=bgcolor, transparent=transparent)
        return Response(result.as_buffer(), content_type=params.format_mime_type)
    
    @staticmethod
    def _bgcolor(params):
        """
        >>> WMSImageExceptionHandler._bgcolor({'bgcolor': '0Xf0ea42'})
        '#f0ea42'
        >>> WMSImageExceptionHandler._bgcolor({})
        '#ffffff'
        """
        if 'bgcolor' in params:
            color = params['bgcolor']
            if color.lower().startswith('0x'):
                color = '#' + color[2:]
        else:
            color = '#ffffff'
        return color

class WMSBlankExceptionHandler(WMSImageExceptionHandler):
    """
    Exception handler for blank image exceptions.
    """
    
    def render(self, request_error):
        request_error.message = ''
        return WMSImageExceptionHandler.render(self, request_error)
