import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from . import services


logger = logging.getLogger(__name__)


@require_POST
def preguntar(request):
    try:
        payload = json.loads(request.body or b'{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'El cuerpo debe ser JSON válido.'}, status=400)

    question = payload.get('question') if isinstance(payload, dict) else None
    if not isinstance(question, str) or not question.strip():
        return JsonResponse({'error': 'La pregunta es obligatoria.'}, status=400)

    if not services.is_available():
        return JsonResponse(
            {'error': 'El chatbot no está disponible en este momento.'},
            status=503,
        )

    history = payload.get('history', [])
    try:
        answer = services.responder(question.strip(), history)
    except services.ChatbotUnavailable:
        return JsonResponse(
            {'error': 'El chatbot no está disponible en este momento.'},
            status=503,
        )
    except Exception:
        logger.exception('Chatbot request failed.')
        return JsonResponse(
            {'error': 'No se pudo obtener una respuesta. Intentá nuevamente.'},
            status=503,
        )

    return JsonResponse({'answer': answer})
