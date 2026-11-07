import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from funciones.models import Funcion
from peliculas.models import Pelicula
from salas.models import Sala

from . import services


class PromptContextTests(SimpleTestCase):
    @patch('chatbot.services.get_live_catalog', return_value='LIVE CATALOG')
    @patch('chatbot.services._get_vectorstore')
    def test_context_combines_retrieved_help_and_fresh_catalog(
        self, get_vectorstore, get_live_catalog
    ):
        vectorstore = get_vectorstore.return_value
        vectorstore.similarity_search.return_value = [
            SimpleNamespace(page_content='HELP DOCUMENT CHUNK')
        ]

        context = services.build_context('¿Cómo compro?')

        self.assertIn('LIVE CATALOG', context)
        self.assertIn('HELP DOCUMENT CHUNK', context)
        vectorstore.similarity_search.assert_called_once_with('¿Cómo compro?', k=4)
        get_live_catalog.assert_called_once_with()

    def test_prompt_declares_all_inputs_and_grounding_rules(self):
        self.assertIn('{context}', services.PROMPT_TEMPLATE)
        self.assertIn('{history}', services.PROMPT_TEMPLATE)
        self.assertIn('{question}', services.PROMPT_TEMPLATE)
        self.assertIn('No inventes', services.PROMPT_TEMPLATE)

    @patch('chatbot.services.is_available', return_value=True)
    @patch('chatbot.services._get_chain')
    def test_responder_sends_question_and_history_to_chain(
        self, get_chain, _is_available
    ):
        get_chain.return_value.invoke.return_value = 'Respuesta de prueba.'
        history = [{'role': 'user', 'content': 'Hola'}]

        answer = services.responder('¿Qué hay en cartelera?', history)

        self.assertEqual(answer, 'Respuesta de prueba.')
        get_chain.return_value.invoke.assert_called_once_with(
            {'question': '¿Qué hay en cartelera?', 'history': history}
        )

    def test_history_keeps_only_recent_valid_messages(self):
        history = [
            {'role': 'user', 'content': f'question {number}'}
            for number in range(12)
        ]
        formatted = services.format_history(history)

        self.assertNotIn('question 1\n', formatted)
        self.assertIn('question 2', formatted)
        self.assertIn('question 11', formatted)


class LiveCatalogSnapshotTests(TestCase):
    def setUp(self):
        self.sala = Sala.objects.create(
            nombre='Sala Chatbot',
            distribucion={'filas': ['AAA']},
            tipo_sala='2D',
            tipo_sonido='Estéreo',
            capacidad=3,
        )
        self.pelicula = Pelicula.objects.create(
            titulo='Película de prueba',
            imagen_portada='imgs/chatbot-test.jpg',
            genero='Drama',
            duracion_minutos=100,
            descripcion='Película creada para una prueba.',
            clasificacion='ATP',
            fecha_estreno=timezone.localdate() + timedelta(days=1),
            url_trailer='https://example.com/trailer',
            en_cartelera=True,
        )

    def test_snapshot_includes_current_active_functions_and_movie_metadata(self):
        start = timezone.now() + timedelta(days=1)
        function = Funcion.objects.create(
            funcion_activa=True,
            inicio=start,
            fin=start + timedelta(hours=2),
            idioma='Español',
            subtitulada=False,
            distribucion={'filas': ['AAA']},
            disponibilidad=3,
            precio_entrada='2500.00',
            pelicula=self.pelicula,
            sala=self.sala,
        )

        snapshot = services.get_live_catalog()

        self.assertIn(self.pelicula.titulo, snapshot)
        self.assertIn('La película más nueva', snapshot)
        self.assertIn(f'Función {function.pk}', snapshot)
        self.assertIn(self.sala.nombre, snapshot)
        self.assertIn('2500.00', snapshot)
        self.assertIn('entradas disponibles 3', snapshot)

    def test_snapshot_reports_empty_cartelera(self):
        Pelicula.objects.filter(pk=self.pelicula.pk).update(en_cartelera=False)

        self.assertIn('No hay películas actualmente en cartelera', services.get_live_catalog())


class ChatbotEndpointTests(SimpleTestCase):
    url = reverse('chatbot:preguntar')

    def test_missing_question_returns_400(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'question': '  '}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            self.url,
            data='{invalid',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    @patch('chatbot.views.services.is_available', return_value=False)
    @patch('chatbot.views.services.responder')
    def test_unconfigured_chatbot_returns_503(self, responder, _is_available):
        response = self.client.post(
            self.url,
            data=json.dumps({'question': '¿Qué hay en cartelera?'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn('error', response.json())
        responder.assert_not_called()

    @patch('chatbot.views.services.is_available', return_value=True)
    @patch('chatbot.views.services.responder', return_value='Hay una película.')
    def test_valid_question_returns_json_answer(self, responder, _is_available):
        history = [{'role': 'user', 'content': 'Hola'}]
        response = self.client.post(
            self.url,
            data=json.dumps({'question': '¿Qué hay en cartelera?', 'history': history}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'answer': 'Hay una película.'})
        responder.assert_called_once_with('¿Qué hay en cartelera?', history)

    def test_endpoint_rejects_get(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
