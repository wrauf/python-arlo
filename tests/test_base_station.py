"""The tests for the PyArlo platform."""
import unittest
from mock import Mock, patch, MagicMock
from pyarlo import ArloBaseStation, PyArlo
from tests.common import (
    load_fixture,
    load_base_properties as load_base_props,
    load_camera_properties as load_camera_props,
    load_camera_rules,
    load_camera_schedule,
    load_ambient_sensor_data,
    load_audio_playback_status,
    load_extended_properties
)

import requests_mock

from pyarlo.const import (
    DEVICES_ENDPOINT,
    LIBRARY_ENDPOINT,
    LOGIN_ENDPOINT,
    RESOURCES,
    NOTIFY_ENDPOINT
)

USERNAME = "foo"
PASSWORD = "bar"
USERID = "999-123456"


class TestArloBaseStation(unittest.TestCase):
    """Tests for ArloBaseStation component."""

    def load_base_station(self, mock):
        mock.post(LOGIN_ENDPOINT,
                  text=load_fixture("pyarlo_authentication.json"))
        mock.get(DEVICES_ENDPOINT, text=load_fixture("pyarlo_devices.json"))
        mock.post(LIBRARY_ENDPOINT, text=load_fixture("pyarlo_videos.json"))
        arlo = PyArlo(USERNAME, PASSWORD, days=1)
        base_station = arlo.base_stations[0]
        mock.post(NOTIFY_ENDPOINT.format(base_station.device_id),
                  text=load_fixture("pyarlo_success.json"))
        return base_station

    @requests_mock.Mocker()
    def test_properties(self, mock):
        """Test ArloBaseStation properties."""
        base = self.load_base_station(mock)
        self.assertIsInstance(base, ArloBaseStation)
        self.assertTrue(base.__repr__().startswith("<ArloBaseStation:"))
        self.assertEqual(base.device_id, "48B14CBBBBBBB")
        self.assertEqual(base.device_type, "basestation")
        self.assertEqual(base.model_id, "VMB3010")
        self.assertEqual(base.hw_version, "VMB3010r2")
        self.assertEqual(base.timezone, "America/New_York")
        self.assertEqual(base.unique_id, "235-48B14CBBBBBBB")
        self.assertEqual(base.user_id, USERID)
        self.assertEqual(base.user_role, "ADMIN")
        self.assertEqual(base.xcloud_id, "1005-123-999999")

        self.assertEqual(set(base.available_resources), set(RESOURCES.keys()))

    @requests_mock.Mocker()
    def test_is_motion_detection_enabled(self, mock):
        """Test ArloBaseStation.is_motion_detection_enabled properties."""
        with patch.object(ArloBaseStation, 'mode') as mocked_mode:
            mocked_mode.__get__ = Mock(return_value='armed')
            base = self.load_base_station(mock)
            self.assertTrue(base.is_motion_detection_enabled)

        with patch.object(ArloBaseStation, 'mode') as mocked_mode:
            mocked_mode.__get__ = Mock(return_value='disarmed')
            base = self.load_base_station(mock)
            self.assertFalse(base.is_motion_detection_enabled)

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_base_props)
    def test_get_properties(self, mock):
        """Test ArloBaseStation.get_basestation_properties."""
        base = self.load_base_station(mock)
        base_properties = base.properties
        mocked_properties = load_base_props()
        self.assertEqual(base_properties, mocked_properties["properties"])

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_props)
    @patch.object(ArloBaseStation, "get_ambient_sensor_data", MagicMock())
    def test_camera_properties(self, mock):
        """Test ArloBaseStation.get_cameras_properties."""
        base = self.load_base_station(mock)
        camera_properties = base.camera_properties
        mocked_properties = load_camera_props()
        self.assertEqual(camera_properties, mocked_properties["properties"])

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_props)
    def test_battery_level(self, mock):
        """Test ArloBaseStation.get_cameras_battery_level."""
        base = self.load_base_station(mock)
        self.assertEqual(
            base.get_cameras_battery_level(),
            {"48B14C1299999": 95, "48B14CAAAAAAA": 77}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_props)
    def test_signal_strength(self, mock):
        """Test ArloBaseStation.get_cameras_signal_strength."""
        base = self.load_base_station(mock)
        self.assertEqual(
            base.get_cameras_signal_strength(),
            {"48B14C1299999": 4, "48B14CAAAAAAA": 3}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", load_camera_rules)
    def test_camera_rules(self, mock):
        """Test ArloBaseStation.get_cameras_rules."""
        base = self.load_base_station(mock)
        camera_rules = base.get_cameras_rules()
        mocked_rules = load_camera_rules()
        self.assertEqual(camera_rules, mocked_rules["properties"])

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", load_camera_schedule)
    def test_camera_schedule(self, mock):
        """Test ArloBaseStation.get_cameras_schedule."""
        base = self.load_base_station(mock)
        camera_schedule = base.get_cameras_schedule()
        mocked_schedules = load_camera_schedule()
        self.assertEqual(camera_schedule, mocked_schedules["properties"])

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", load_ambient_sensor_data)
    def test_ambient_sensor_data(self, mock):
        """Test ArloBaseStation.ambient_sensor_data."""
        base = self.load_base_station(mock)
        sensor_data = base.ambient_sensor_data
        self.assertEqual(len(sensor_data), 2010)
        self.assertEqual(base.ambient_temperature, 24.6)
        self.assertEqual(base.ambient_humidity, 37.2)
        self.assertEqual(base.ambient_air_quality, 11.2)

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", lambda x, y: None)
    def test_ambient_sensor_data_none(self, mock):
        """Test ArloBaseStation.get_ambient_sensor_data HTTP error."""
        base = self.load_base_station(mock)
        result = base.get_ambient_sensor_data()
        self.assertEqual(result, None)

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", load_ambient_sensor_data)
    def test_latest_sensor_statistic(self, mock):
        """Test ArloBaseStation.get_latest_ambient_sensor_statistic."""
        base = self.load_base_station(mock)
        temperature = base.get_latest_ambient_sensor_statistic("temperature")
        self.assertEqual(temperature, 24.6)

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", lambda x, y: None)
    def test_latest_sensor_statistic_none(self, mock):
        """Test ArloBaseStation.get_latest_ambient_sensor_statistic None."""
        base = self.load_base_station(mock)
        temperature = base.get_latest_ambient_sensor_statistic("temperature")
        self.assertEqual(temperature, None)

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", load_audio_playback_status)
    def test_audio_playback_status(self, mock):
        """Test ArloBaseStation.get_audio_playback_status."""
        base = self.load_base_station(mock)
        expected = load_audio_playback_status()
        actual = base.get_audio_playback_status()
        self.assertEqual(expected, actual)

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_play_track(self, mock):
        """Test ArloBaseStation.play_track."""
        base = self.load_base_station(mock)
        base.play_track()
        base.publish.assert_called_once_with(
            action='playTrack',
            resource='audioPlayback/player',
            publish_response=False,
            properties={
                'trackId': '229dca67-7e3c-4a5f-8f43-90e1a9bffc38',
                'position': 0
            }
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_pause_track(self, mock):
        """Test ArloBaseStation.pause_track."""
        base = self.load_base_station(mock)
        base.pause_track()
        base.publish.assert_called_once_with(
            action='pause',
            resource='audioPlayback/player',
            publish_response=False
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_skip_track(self, mock):
        """Test ArloBaseStation.skip_track."""
        base = self.load_base_station(mock)
        base.skip_track()
        base.publish.assert_called_once_with(
            action='nextTrack',
            resource='audioPlayback/player',
            publish_response=False
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_set_music_mode_continuous(self, mock):
        """Test ArloBaseStation.set_music_loop_mode_continuous."""
        base = self.load_base_station(mock)
        base.set_music_loop_mode_continuous()
        base.publish.assert_called_once_with(
            action='set',
            resource='audioPlayback/config',
            publish_response=False,
            properties={'config': {'loopbackMode': 'continuous'}}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_set_music_mode_single(self, mock):
        """Test ArloBaseStation.set_music_loop_mode_single."""
        base = self.load_base_station(mock)
        base.set_music_loop_mode_single()
        base.publish.assert_called_once_with(
            action='set',
            resource='audioPlayback/config',
            publish_response=False,
            properties={'config': {'loopbackMode': 'singleTrack'}}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_shuffle_on(self, mock):
        """Test ArloBaseStation.set_shuffle_on."""
        base = self.load_base_station(mock)
        base.set_shuffle_on()
        base.publish.assert_called_once_with(
            action='set',
            resource='audioPlayback/config',
            publish_response=False,
            properties={'config': {'shuffleActive': True}}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_shuffle_off(self, mock):
        """Test ArloBaseStation.set_shuffle_off."""
        base = self.load_base_station(mock)
        base.set_shuffle_off()
        base.publish.assert_called_with(
            action='set',
            resource='audioPlayback/config',
            publish_response=False,
            properties={'config': {'shuffleActive': False}}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_set_volume(self, mock):
        """Test ArloBaseStation.set_volume."""
        base = self.load_base_station(mock)
        base.set_volume(mute=False, volume=100)
        base.publish.assert_called_once_with(
            action='set',
            resource='cameras/48B14CBBBBBBB',
            publish_response=False,
            properties={'speaker': {'mute': False, 'volume': 100}}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_night_light_on(self, mock):
        """Test ArloBaseStation.set_night_light_on."""
        base = self.load_base_station(mock)
        base.set_night_light_on()
        base.publish.assert_called_once_with(
            action='set',
            resource='cameras/48B14CBBBBBBB',
            publish_response=False,
            properties={'nightLight': {'enabled': True}}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_night_light_off(self, mock):
        """Test ArloBaseStation.set_night_light_off."""
        base = self.load_base_station(mock)
        base.set_night_light_off()
        base.publish.assert_called_once_with(
            action='set',
            resource='cameras/48B14CBBBBBBB',
            publish_response=False,
            properties={'nightLight': {'enabled': False}}
        )

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    def test_night_light_brightness(self, mock):
        """Test ArloBaseStation.set_night_light_brightness."""
        base = self.load_base_station(mock)
        base.set_night_light_brightness(100)
        base.publish.assert_called_once_with(
            action='set',
            resource='cameras/48B14CBBBBBBB',
            publish_response=False,
            properties={'nightLight': {'brightness': 100}}
        )

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", load_extended_properties)
    def test_get_speaker_muted(self, mock):
        """Test ArloBaseStation.get_speaker_muted."""
        base = self.load_base_station(mock)
        result = base.get_speaker_muted()
        self.assertEqual(result, False)

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", load_extended_properties)
    def test_get_speaker_volume(self, mock):
        """Test ArloBaseStation.get_speaker_volume."""
        base = self.load_base_station(mock)
        result = base.get_speaker_volume()
        self.assertEqual(result, 100)

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", load_extended_properties)
    def test_get_night_light_state_off(self, mock):
        """Test ArloBaseStation.get_speaker_volume."""
        base = self.load_base_station(mock)
        result = base.get_night_light_state()
        self.assertEqual(result, 'off')

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", lambda x, y: {
            'properties': {
                'nightLight': {
                    'enabled': True
                }
            }
        })
    def test_get_night_light_state_on(self, mock):
        """Test ArloBaseStation.get_speaker_volume."""
        base = self.load_base_station(mock)
        result = base.get_night_light_state()
        self.assertEqual(result, 'on')

    @requests_mock.Mocker()
    @patch.object(
        ArloBaseStation, "publish_and_get_event", load_extended_properties)
    def test_get_night_light_brightness(self, mock):
        """Test ArloBaseStation.get_night_light_brightness."""
        base = self.load_base_station(mock)
        result = base.get_night_light_brightness()
        self.assertEqual(result, 200)

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", lambda x, y: None)
    def test_extended_properties_none(self, mock):
        """Test extended properties when API returns None."""
        base = self.load_base_station(mock)
        self.assertEqual(base.get_speaker_muted(), None)
        self.assertEqual(base.get_speaker_volume(), None)
        self.assertEqual(base.get_night_light_state(), None)
        self.assertEqual(base.get_night_light_brightness(), None)

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish_and_get_event", lambda x, y: {
        'properties': {
            'speaker': None,
            'nightLight': None
        }
    })
    def test_extended_properties_empty(self, mock):
        """Test extended properties when API is missing dictionary keys."""
        base = self.load_base_station(mock)
        self.assertEqual(base.get_speaker_muted(), None)
        self.assertEqual(base.get_speaker_volume(), None)
        self.assertEqual(base.get_night_light_state(), None)
        self.assertEqual(base.get_night_light_brightness(), None)

    @requests_mock.Mocker()
    @patch.object(ArloBaseStation, "publish", MagicMock())
    @patch.object(ArloBaseStation, "update", MagicMock())
    def test_camera_enabled(self, mock):
        """Test ArloBaseStation.set_camera_enabled."""
        base = self.load_base_station(mock)
        base.set_camera_enabled("48B14CBBBBBBB", True)
        base.publish.assert_called_once_with(
            action='set',
            resource='privacy',
            camera_id='48B14CBBBBBBB',
            mode=True,
            publish_response=True
        )
        base.update.assert_called_once_with()

    @requests_mock.Mocker()
    def test_parse_statistic(self, mock):
        """Test ArloBaseStation._parse_statistic"""
        base = self.load_base_station(mock)
        data = b'\x80\x00'
        # pylint: disable=W0212
        result = base._parse_statistic(data, 0)
        # pylint: enable=W0212
        self.assertEqual(result, None)
