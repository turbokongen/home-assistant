"""
Support for MQTT cover devices.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/cover.mqtt/
"""
import logging

import voluptuous as vol

import homeassistant.components.mqtt as mqtt
from homeassistant.components.cover import CoverDevice
from homeassistant.const import (
    CONF_NAME, CONF_VALUE_TEMPLATE, CONF_OPTIMISTIC, STATE_OPEN,
    STATE_CLOSED)
from homeassistant.components.mqtt import (
    CONF_STATE_TOPIC, CONF_COMMAND_TOPIC, CONF_QOS, CONF_RETAIN)
from homeassistant.helpers import template
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['mqtt']

CONF_PAYLOAD_OPEN = 'payload_open'
CONF_PAYLOAD_CLOSE = 'payload_close'
CONF_PAYLOAD_STOP = 'payload_stop'
CONF_STATE_OPEN = 'state_open'
CONF_STATE_CLOSED = 'state_closed'

DEFAULT_NAME = "MQTT Cover"
DEFAULT_PAYLOAD_OPEN = "OPEN"
DEFAULT_PAYLOAD_CLOSE = "CLOSE"
DEFAULT_PAYLOAD_STOP = "STOP"
DEFAULT_OPTIMISTIC = False
DEFAULT_RETAIN = False

PLATFORM_SCHEMA = mqtt.MQTT_RW_PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PAYLOAD_OPEN, default=DEFAULT_PAYLOAD_OPEN): cv.string,
    vol.Optional(CONF_PAYLOAD_CLOSE, default=DEFAULT_PAYLOAD_CLOSE): cv.string,
    vol.Optional(CONF_PAYLOAD_STOP, default=DEFAULT_PAYLOAD_STOP): cv.string,
    vol.Optional(CONF_STATE_OPEN, default=STATE_OPEN): cv.string,
    vol.Optional(CONF_STATE_CLOSED, default=STATE_CLOSED): cv.string,
    vol.Optional(CONF_OPTIMISTIC, default=DEFAULT_OPTIMISTIC): cv.boolean,
    vol.Optional(CONF_RETAIN, default=DEFAULT_RETAIN): cv.boolean,

})


def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Add MQTT Cover."""
    add_devices_callback([MqttCover(
        hass,
        config[CONF_NAME],
        config.get(CONF_STATE_TOPIC),
        config[CONF_COMMAND_TOPIC],
        config[CONF_QOS],
        config[CONF_RETAIN],
        config[CONF_STATE_OPEN],
        config[CONF_STATE_CLOSED],
        config[CONF_PAYLOAD_OPEN],
        config[CONF_PAYLOAD_CLOSE],
        config[CONF_PAYLOAD_STOP],
        config[CONF_OPTIMISTIC],
        config.get(CONF_VALUE_TEMPLATE)
    )])


# pylint: disable=too-many-arguments, too-many-instance-attributes
class MqttCover(CoverDevice):
    """Representation of a cover that can be controlled using MQTT."""

    def __init__(self, hass, name, state_topic, command_topic, qos,
                 retain, state_open, state_closed, payload_open, payload_close,
                 payload_stop, optimistic, value_template):
        """Initialize the cover."""
        self._position = None
        self._state = None
        self._hass = hass
        self._name = name
        self._state_topic = state_topic
        self._command_topic = command_topic
        self._qos = qos
        self._payload_open = payload_open
        self._payload_close = payload_close
        self._payload_stop = payload_stop
        self._state_open = state_open
        self._state_closed = state_closed
        self._retain = retain
        self._optimistic = optimistic or state_topic is None

        def message_received(topic, payload, qos):
            """A new MQTT message has been received."""
            if value_template is not None:
                payload = template.render_with_possible_json_value(
                    hass, value_template, payload)
            if payload == self._state_open:
                self._state = True
                self.update_ha_state()
            elif payload == self._state_closed:
                self._state = False
                self.update_ha_state()
            elif payload.isnumeric() and 0 <= int(payload) <= 100:
                self._state = int(payload)
                self._position = int(payload)
                self.update_ha_state()
            else:
                _LOGGER.warning(
                    "Payload is not True or False or"
                    " integer(0-100) %s", payload)
        if self._state_topic is None:
            # Force into optimistic mode.
            self._optimistic = True
        else:
            mqtt.subscribe(hass, self._state_topic, message_received,
                           self._qos)

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        if self.current_cover_position is not None:
            if self.current_cover_position > 0:
                return False
            else:
                return True

    @property
    def current_cover_position(self):
        """Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        return self._position

    def open_cover(self, **kwargs):
        """Move the cover up."""
        mqtt.publish(self.hass, self._command_topic, self._payload_open,
                     self._qos, self._retain)
        if self._optimistic:
            # Optimistically assume that cover has changed state.
            self._state = 100
            self.update_ha_state()

    def close_cover(self, **kwargs):
        """Move the cover down."""
        mqtt.publish(self.hass, self._command_topic, self._payload_close,
                     self._qos, self._retain)
        if self._optimistic:
            # Optimistically assume that cover has changed state.
            self._state = 0
            self.update_ha_state()

    def stop_cover(self, **kwargs):
        """Stop the device."""
        mqtt.publish(self.hass, self._command_topic, self._payload_stop,
                     self._qos, self._retain)
