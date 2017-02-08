"""Zwave workarounds."""
from . import const

# Manufacturers
FIBARO = 0x010f
PHILIO = 0x013c
REMOTEC = 0x5254
WENZHOU = 0x0118

# Product IDs
PHILIO_SLIM_SENSOR = 0x0002
PHILIO_3_IN_1_SENSOR_GEN_4 = 0x000d
REMOTEC_ZXT_120 = 0x8377

# Product Types
FGFS101_FLOOD_SENSOR_TYPE = 0x0b00
PHILIO_SENSOR = 0x0002

# Mapping devices
PHILIO_SLIM_SENSOR_MOTION = (PHILIO, PHILIO_SENSOR, PHILIO_SLIM_SENSOR, 0)
PHILIO_3_IN_1_SENSOR_GEN_4_MOTION = (
    PHILIO, PHILIO_SENSOR, PHILIO_3_IN_1_SENSOR_GEN_4, 0)
REMOTEC_ZXT_120_THERMOSTAT = (REMOTEC, REMOTEC_ZXT_120, 101)
WENZHOU_SLIM_SENSOR_MOTION = (WENZHOU, PHILIO_SENSOR, PHILIO_SLIM_SENSOR, 0)

# Workarounds
WORKAROUND_NO_OFF_EVENT = 'trigger_no_off_event'
WORKAROUND_ZXT_120 = 'zxt_120'

# List of workarounds by (manufacturer_id, product_type, product_id, index)
DEVICE_MAPPINGS = {
    PHILIO_SLIM_SENSOR_MOTION: WORKAROUND_NO_OFF_EVENT,
    PHILIO_3_IN_1_SENSOR_GEN_4_MOTION: WORKAROUND_NO_OFF_EVENT,
    REMOTEC_ZXT_120_THERMOSTAT: WORKAROUND_ZXT_120,
    WENZHOU_SLIM_SENSOR_MOTION: WORKAROUND_NO_OFF_EVENT,
}

# Component mapping devices
FIBARO_FGFS101_SENSOR_ALARM = (
    FIBARO, FGFS101_FLOOD_SENSOR_TYPE, const.COMMAND_CLASS_SENSOR_ALARM)

# List of component workarounds by
# (manufacturer_id, product_type, command_class)
DEVICE_COMPONENT_MAPPING = {
    FIBARO_FGFS101_SENSOR_ALARM: 'binary_sensor',
}


def get_device_component_mapping(value):
    """Get mapping of value to another component."""
    if (value.node.manufacturer_id.strip() and
            value.node.product_type.strip()):
        manufacturer_id = int(value.node.manufacturer_id, 16)
        product_type = int(value.node.product_type, 16)
        return DEVICE_COMPONENT_MAPPING.get(
            (manufacturer_id, product_type, value.command_class))

    return None


def get_device_mapping(value):
    """Get mapping of value to a workaround."""
    if (value.node.manufacturer_id.strip() and
            value.node.product_id.strip() and
            value.node.product_type.strip()):
        manufacturer_id = int(value.node.manufacturer_id, 16)
        product_type = int(value.node.product_type, 16)
        product_id = int(value.node.product_id, 16)
        return DEVICE_MAPPINGS.get(
            (manufacturer_id, product_type, product_id, value.index))

    return None
