from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code
        logger.error(f"API Error: {response.data}")
    else:
        # Para errores no manejados por DRF
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)

    return response
