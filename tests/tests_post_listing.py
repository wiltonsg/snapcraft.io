import unittest
import responses
import json

from tests.endpoint_testing import BaseTestCases


class PostListingPageNotAuth(BaseTestCases.EndpointLoggedOut):
    def setUp(self):
        snap_name = "test-snap"
        endpoint_url = '/account/snaps/{}/listing'.format(snap_name)

        super().setUp(
            snap_name=snap_name,
            endpoint_url=endpoint_url,
            method_endpoint='POST')


class PostMetadataListingPage(BaseTestCases.EndpointLoggedIn):
    def setUp(self):
        self.snap_id = 'complexId'

        snap_name = "test-snap"
        endpoint_url = '/account/snaps/{}/listing'.format(snap_name)
        api_url = (
            'https://dashboard.snapcraft.io/dev/api/'
            'snaps/{}/metadata').format(
                self.snap_id)

        changes = {
            "contact": "contact-adress"
        }
        data = {
            'changes': json.dumps(changes),
            'snap_id': self.snap_id
        }

        super().setUp(
            snap_name=snap_name,
            api_url=api_url,
            endpoint_url=endpoint_url,
            method_api='PUT',
            method_endpoint='POST',
            data=data)

    @responses.activate
    def test_post_no_data(self):
        response = self.client.post(
            self.endpoint_url,
        )

        assert response.status_code == 302
        assert response.location == self._get_location()

    @responses.activate
    def test_update_invalid_field(self):
        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': '{"dumb_field": "this is a dumb field"}'
            },
        )

        assert 0 == len(responses.calls)
        assert response.status_code == 302
        assert response.location == self._get_location()

    @responses.activate
    def test_update_valid_field(self):
        responses.add(
            responses.PUT, self.api_url,
            json={}, status=200)

        changes = {
            "contact": "contact-adress"
        }

        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': json.dumps(changes),
                'snap_id': self.snap_id
            },
        )

        self.assertEqual(1, len(responses.calls))
        called = responses.calls[0]
        self.assertEqual(
            self.api_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))
        self.assertEqual(
            b'{"contact": "contact-adress"}',
            called.request.body)

        assert response.status_code == 302
        assert response.location == self._get_location()

    @responses.activate
    def test_update_description_with_carriage_return(self):
        responses.add(
            responses.PUT, self.api_url,
            json={}, status=200)

        changes = {
            "description": "This is a description\r\n"
        }

        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': json.dumps(changes),
                'snap_id': self.snap_id
            },
        )

        self.assertEqual(1, len(responses.calls))
        called = responses.calls[0]
        self.assertEqual(
            self.api_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))
        self.assertEqual(
            b'{"description": "This is a description\\n"}',
            called.request.body)

        assert response.status_code == 302
        assert response.location == self._get_location()

    @responses.activate
    def test_update_no_metric_blacklist(self):
        responses.add(
            responses.PUT, self.api_url,
            json={}, status=200)

        changes = {
            "public_metrics_blacklist": ""
        }

        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': json.dumps(changes),
                'snap_id': self.snap_id
            },
        )

        self.assertEqual(1, len(responses.calls))
        called = responses.calls[0]
        self.assertEqual(
            self.api_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))
        self.assertEqual(
            b'{"public_metrics_blacklist": []}',
            called.request.body)

        assert response.status_code == 302
        assert response.location == self._get_location()

    @responses.activate
    def test_update_one_metric_blacklist(self):
        responses.add(
            responses.PUT, self.api_url,
            json={}, status=200)

        changes = {
            "public_metrics_blacklist": "metric"
        }

        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': json.dumps(changes),
                'snap_id': self.snap_id
            },
        )

        self.assertEqual(1, len(responses.calls))
        called = responses.calls[0]
        self.assertEqual(
            self.api_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))
        self.assertEqual(
            b'{"public_metrics_blacklist": ["metric"]}',
            called.request.body)

        assert response.status_code == 302
        assert response.location == self._get_location()

    @responses.activate
    def test_update_multiple_metrics_blacklist(self):
        responses.add(
            responses.PUT, self.api_url,
            json={}, status=200)

        changes = {
            "public_metrics_blacklist": "metric1,metric2"
        }

        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': json.dumps(changes),
                'snap_id': self.snap_id
            },
        )

        self.assertEqual(1, len(responses.calls))
        called = responses.calls[0]
        self.assertEqual(
            self.api_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))
        self.assertEqual(
            b'{"public_metrics_blacklist": ["metric1", "metric2"]}',
            called.request.body)

        assert response.status_code == 302
        assert response.location == self._get_location()

    @responses.activate
    def test_return_error_udpate_one_field(self):
        metadata_payload = {
            'error_list': [
                {
                    'code': 'code',
                    'message': 'message'
                }
            ]
        }

        responses.add(
            responses.PUT, self.api_url,
            json=metadata_payload, status=500)

        info_url = 'https://dashboard.snapcraft.io/dev/api/snaps/info/{}'
        info_url = info_url.format(
            self.snap_name
        )

        payload = {
            'snap_id': self.snap_id,
            'snap_name': self.snap_name,
            'title': 'Snap title',
            'summary': 'This is a summary',
            'description': 'This is a description',
            'license': 'license',
            'media': [],
            'publisher': {
                'display-name': 'The publisher'
            },
            'private': True,
            'channel_maps_list': [{'map': [{'info': 'info'}]}],
            'contact': 'contact adress',
            'website': 'website_url',
            'public_metrics_enabled': True,
            'public_metrics_blacklist': True,
        }

        responses.add(
            responses.GET, info_url,
            json=payload, status=200)

        changes = {
            "description": "This is an updated description"
        }

        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': json.dumps(changes),
                'snap_id': self.snap_id
            },
        )

        self.assertEqual(2, len(responses.calls))
        called = responses.calls[0]
        self.assertEqual(
            self.api_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))
        self.assertEqual(
            b'{"description": "This is an updated description"}',
            called.request.body
        )
        called = responses.calls[1]
        self.assertEqual(
            info_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('publisher/listing.html')

        self.assert_context('snap_id', self.snap_id)
        self.assert_context('snap_name', self.snap_name)
        # udpated field
        self.assert_context('description', 'This is an updated description')

        self.assert_context('snap_title', 'Snap title')
        self.assert_context('summary', 'This is a summary')
        self.assert_context('license', 'license')
        self.assert_context('icon_url', None)
        self.assert_context('publisher_name', 'The publisher')
        self.assert_context('screenshot_urls', [])
        self.assert_context('contact', 'contact adress')
        self.assert_context('website', 'website_url')
        self.assert_context('public_metrics_enabled', True)
        self.assert_context('public_metrics_blacklist', True)
        self.assert_context('is_on_stable', False)

    @responses.activate
    def test_return_error_udpate_all_field(self):
        metadata_payload = {
            'error_list': [
                {
                    'code': 'code',
                    'message': 'message'
                }
            ]
        }

        responses.add(
            responses.PUT, self.api_url,
            json=metadata_payload, status=500)

        info_url = 'https://dashboard.snapcraft.io/dev/api/snaps/info/{}'
        info_url = info_url.format(
            self.snap_name
        )

        payload = {
            'snap_id': self.snap_id,
            'snap_name': self.snap_name,
            'title': 'Snap title',
            'summary': 'This is a summary',
            'description': 'This is a description',
            'license': 'license',
            'media': [],
            'publisher': {
                'display-name': 'The publisher'
            },
            'private': True,
            'channel_maps_list': [{'map': [{'info': 'info'}]}],
            'contact': 'contact adress',
            'website': 'website_url',
            'public_metrics_enabled': True,
            'public_metrics_blacklist': True,
        }

        responses.add(
            responses.GET, info_url,
            json=payload, status=200)

        changes = {
            "snap_title": "New title",
            "summary": "New summary",
            "description": "New description",
            "icon_url": None,
            "publisher_name": "New publisher",
            "screenshot_urls": [],
            "contact": "New contact",
            "website": "New website",
            "public_metrics_enabled": False,
            "public_metrics_blacklist": "new metric1,new metric2",
        }

        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': json.dumps(changes),
                'snap_id': self.snap_id
            },
        )

        self.assertEqual(2, len(responses.calls))
        called = responses.calls[0]
        self.assertEqual(
            self.api_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))
        called = responses.calls[1]
        self.assertEqual(
            info_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('publisher/listing.html')

        # Not updatable fields
        self.assert_context('snap_id', self.snap_id)
        self.assert_context('snap_name', self.snap_name)
        self.assert_context('public_metrics_enabled', True)
        self.assert_context('public_metrics_blacklist', True)
        self.assert_context('license', 'license')
        self.assert_context('icon_url', None)
        self.assert_context('publisher_name', 'The publisher')
        self.assert_context('screenshot_urls', [])
        self.assert_context('snap_title', 'Snap title')
        self.assert_context('is_on_stable', False)

        # All updatable fields
        self.assert_context('summary', 'New summary')
        self.assert_context('description', 'New description')
        self.assert_context('contact', 'New contact')
        self.assert_context('website', 'New website')

    @responses.activate
    def test_return_error_invalid_field(self):
        metadata_payload = {
            'error_list': [
                {
                    'code': 'invalid-field',
                    'message': 'error message',
                    'extra': {'name': 'description'}
                }
            ]
        }

        responses.add(
            responses.PUT, self.api_url,
            json=metadata_payload, status=500)

        info_url = 'https://dashboard.snapcraft.io/dev/api/snaps/info/{}'
        info_url = info_url.format(
            self.snap_name
        )

        payload = {
            'snap_id': self.snap_id,
            'snap_name': self.snap_name,
            'title': 'Snap title',
            'summary': 'This is a summary',
            'description': 'This is a description',
            'license': 'license',
            'media': [],
            'publisher': {
                'display-name': 'The publisher'
            },
            'private': True,
            'channel_maps_list': [{'map': [{'info': 'info'}]}],
            'contact': 'contact adress',
            'website': 'website_url',
            'public_metrics_enabled': True,
            'public_metrics_blacklist': True,
        }

        responses.add(
            responses.GET, info_url,
            json=payload, status=200)

        changes = {
            "description": "This is an updated description",
        }

        response = self.client.post(
            self.endpoint_url,
            data={
                'changes': json.dumps(changes),
                'snap_id': self.snap_id
            },
        )

        self.assertEqual(2, len(responses.calls))
        called = responses.calls[0]
        self.assertEqual(
            self.api_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))
        called = responses.calls[1]
        self.assertEqual(
            info_url,
            called.request.url)
        self.assertEqual(
            self.authorization, called.request.headers.get('Authorization'))

        self.assertEqual(response.status_code, 200)
        self.assert_template_used('publisher/listing.html')

        self.assert_context('field_errors', {
            'description': 'error message'
        })


if __name__ == '__main__':
    unittest.main()
