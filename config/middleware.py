
import logging
from django.conf import settings
from django.shortcuts import render



class ErrorHandler:

    error_pages = {
        404: "errors/404.html",
        403: "errors/403.html",
        500: "errors/500.html",
        503: "errors/503.html",
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)  # Set up logging

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)
        try:
           
            response = self.get_response(request)

            status_code = response.status_code

            if status_code in self.error_pages:
                return render(request, self.error_pages[status_code], status=status_code)
            return response
                
        except Exception as e:
            # Log the unexpected exception for debugging purposes
            self.logger.error("Unhandled exception occurred: %s", e, exc_info=True)
            
            # Render a generic error page for unexpected exceptions
            return render(request, "errors/500.html", status=500)


        