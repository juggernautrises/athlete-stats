from django.test import TestCase
from stats.views import SpongeBobView
from rest_framework.test import APIRequestFactory


class SpongeBobTestCase(TestCase):

    def test_no_input(self):
        factory = APIRequestFactory()
        view = SpongeBobView.as_view()
        request = factory.post('/api/v1/spongebob/')
        response = view(request)
        self.assertEqual(response.data, '')

    def test_all_letters(self):
        factory = APIRequestFactory()
        view = SpongeBobView.as_view()
        request = factory.post('/api/v1/spongebob/',
                               {'text': 'THISisAlLLETTERS'})
        response = view(request)
        self.assertEqual(response.data, 'tHiSiSaLlLeTtErS')

    def test_all_numbers(self):
        factory = APIRequestFactory()
        view = SpongeBobView.as_view()
        request = factory.post('/api/v1/spongebob/', {'text': 'a1b2c3456'})
        response = view(request)
        self.assertEqual(response.data, 'a1B2c3456')

    def test_all_symbols(self):
        factory = APIRequestFactory()
        view = SpongeBobView.as_view()
        request = factory.post('/api/v1/spongebob/', {'text': '#$@%@$%@$%'})
        response = view(request)
        self.assertEqual(response.data, '#$@%@$%@$%')

    def test_with_spaces(self):
        factory = APIRequestFactory()
        view = SpongeBobView.as_view()
        request = factory.post('/api/v1/spongebob/', {'text': 'ab cd'})
        response = view(request)
        self.assertEqual(response.data, 'aB cD')
