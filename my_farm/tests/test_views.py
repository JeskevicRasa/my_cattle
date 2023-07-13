import os

from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from my_cattle.settings import BASE_DIR
from my_farm.views import upload_picture, GenerateReportView, LivestockMovementReportView
from my_farm.models import Cattle


class UploadPictureViewTestCase(TestCase):
    def setUp(self):
        self.cattle = Cattle.objects.create(name='Test Cattle')

    def test_upload_picture_view(self):
        url = reverse('my_farm:upload_picture', args=[self.cattle.id])
        with open(os.path.join(BASE_DIR, 'test', 'test.jpg'), 'rb') as picture:
            request = self.factory.post(url, {'picture': picture}, format='multipart')
            response = upload_picture(request, cattle_id=self.cattle.id)

        # Assert the response status code and redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('my_farm:one_cattle_info', args=[self.cattle.id]))

        # Assert the updated picture field in the database
        self.cattle.refresh_from_db()
        self.assertIsNotNone(self.cattle.picture)

    def test_upload_picture_view_invalid_data(self):
        url = reverse('my_farm:upload_picture', args=[self.cattle.id])
        response = self.client.post(url, {}, format='multipart')

        # Assert the response status code and template used for rendering
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_farm/upload_picture.html')

        # Assert the picture field remains unchanged in the database
        self.cattle.refresh_from_db()
        self.assertIsNone(self.cattle.picture)


class GenerateReportViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.cattle = Cattle.objects.create(name='Test Cattle', birth_date='2022-01-01')

    def test_generate_report_view_get(self):
        url = reverse('my_farm:generate_report')
        response = self.client.get(url)

        # Assert the response status code and template used for rendering
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_farm/generate_report.html')

    def test_generate_report_view_post(self):
        url = reverse('my_farm:generate_report')
        response = self.client.post(url, {'start_date': '2022-01-01', 'end_date': '2022-12-31'})

        # Assert the response status code and redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('my_farm:report'))

        # Assert the report_data stored in the session
        report_data = self.client.session.get('report_data')
        self.assertIsNotNone(report_data)
        self.assertEqual(report_data['start_date'], '2022-01-01')
        self.assertEqual(report_data['end_date'], '2022-12-31')


class LivestockMovementReportViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.cattle = Cattle.objects.create(name='Test Cattle', birth_date='2022-01-01')

    def test_load_report_data(self):
        view = LivestockMovementReportView()
        url = reverse('my_farm:report')
        response = self.client.get(url)
        request = response.wsgi_request
        request.session['report_data'] = {
            'start_date': '2022-01-01',
            'end_date': '2022-12-31',
        }
        result = view.load_report_data(request)
        self.assertTrue(result)
        self.assertEqual(view.start_date.isoformat(), '2022-01-01')
        self.assertEqual(view.end_date.isoformat(), '2022-12-31')

    def test_load_report_data_no_report_data(self):
        view = LivestockMovementReportView()
        url = reverse('my_farm:report')
        response = self.client.get(url)
        request = response.wsgi_request
        result = view.load_report_data(request)
        self.assertFalse(result)
        self.assertIsNone(view.start_date)
        self.assertIsNone(view.end_date)

    def test_get(self):
        url = reverse('my_farm:report')
        response = self.client.get(url)
        request = response.wsgi_request
        request.session['report_data'] = {
            'start_date': '2022-01-01',
            'end_date': '2022-12-31',
        }
        response = LivestockMovementReportView.as_view()(request)

        # Assert the response status code and template used for rendering
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/livestock_movement_report/')
        self.assertTemplateUsed(response, 'my_farm/livestock_movement_report.html')

        # Assert the context variables
        context = response.context_data
        self.assertEqual(context['start_date'], '2022-01-01')
        self.assertEqual(context['end_date'], '2022-12-31')
        self.assertEqual(len(context['groups']), 0)  # Add assertions for groups when implemented

    def test_post(self):
        url = reverse('my_farm:report')
        response = self.client.post(url, {'start_date': '2022-01-01', 'end_date': '2022-12-31'})
        request = response.wsgi_request
        response = LivestockMovementReportView.as_view()(request)

        # Assert the response status code and redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('my_farm:report'))

        # Assert the report_data stored in the session
        report_data = request.session.get('report_data')
        self.assertIsNotNone(report_data)
        self.assertEqual(report_data['start_date'], '2022-01-01')
        self.assertEqual(report_data['end_date'], '2022-12-31')