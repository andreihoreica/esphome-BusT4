import esphome.codegen as cg
from esphome.components import binary_sensor, cover
import esphome.config_validation as cv

from .. import CONF_BUS_T4_ID, BusT4Component, bus_t4_ns

DEPENDENCIES = ['bus_t4']
AUTO_LOAD = ['binary_sensor']

BusT4Cover = bus_t4_ns.class_('BusT4Cover', cover.Cover, cg.Component)

CONF_OPEN_DURATION = 'open_duration'
CONF_CLOSE_DURATION = 'close_duration'
CONF_AUTO_LEARN_TIMING = 'auto_learn_timing'
CONF_POSITION_REPORT_INTERVAL = 'position_report_interval'
CONF_PHOTOCELL = 'photocell'
CONF_PHOTOCELL_BYTE = 'photocell_byte'
CONF_PHOTOCELL_MASK = 'photocell_mask'
CONF_IO_POLL_INTERVAL = 'io_poll_interval'
CONF_IO_POLL_INTERVAL_CLOSED = 'io_poll_interval_closed'
CONF_IO_POLL_WHILE_MOVING = 'io_poll_while_moving'
CONF_AUTO_CLOSE_STATE = 'auto_close_state'
CONF_PHOTO_CLOSE_STATE = 'photo_close_state'
CONF_AUTO_CLOSE_REGISTER = 'auto_close_register'
CONF_PHOTO_CLOSE_REGISTER = 'photo_close_register'
CONF_CONFIG_READBACK_INTERVAL = 'config_readback_interval'

CONFIG_SCHEMA = (
    cover.cover_schema(BusT4Cover, device_class="gate")
    .extend(cv.COMPONENT_SCHEMA)
    .extend(
        {
            cv.GenerateID(CONF_BUS_T4_ID): cv.use_id(BusT4Component),
            cv.Optional(CONF_OPEN_DURATION, default='20s'): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_CLOSE_DURATION, default='20s'): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_AUTO_LEARN_TIMING, default=True): cv.boolean,
            cv.Optional(CONF_POSITION_REPORT_INTERVAL, default='1s'): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_PHOTOCELL): binary_sensor.binary_sensor_schema(device_class='occupancy'),
            cv.Optional(CONF_PHOTOCELL_BYTE, default=2): cv.int_range(min=0, max=4),
            cv.Optional(CONF_PHOTOCELL_MASK, default=0x04): cv.hex_uint8_t,
            cv.Optional(CONF_IO_POLL_INTERVAL, default='1s'): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_IO_POLL_INTERVAL_CLOSED, default='10s'): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_IO_POLL_WHILE_MOVING, default=False): cv.boolean,
            cv.Optional(CONF_AUTO_CLOSE_STATE): binary_sensor.binary_sensor_schema(entity_category='diagnostic'),
            cv.Optional(CONF_PHOTO_CLOSE_STATE): binary_sensor.binary_sensor_schema(entity_category='diagnostic'),
            cv.Optional(CONF_AUTO_CLOSE_REGISTER, default=0x80): cv.hex_uint8_t,
            cv.Optional(CONF_PHOTO_CLOSE_REGISTER, default=0x84): cv.hex_uint8_t,
            cv.Optional(CONF_CONFIG_READBACK_INTERVAL, default='60s'): cv.positive_time_period_milliseconds,
        }
    )
)

async def to_code(config):
    var = await cover.new_cover(config)
    await cg.register_component(var, config)

    parent = await cg.get_variable(config[CONF_BUS_T4_ID])
    cg.add(var.set_parent(parent))
    
    cg.add(var.set_open_duration(config[CONF_OPEN_DURATION]))
    cg.add(var.set_close_duration(config[CONF_CLOSE_DURATION]))
    cg.add(var.set_auto_learn_timing(config[CONF_AUTO_LEARN_TIMING]))
    cg.add(var.set_position_report_interval(config[CONF_POSITION_REPORT_INTERVAL]))

    cg.add(var.set_photocell_byte(config[CONF_PHOTOCELL_BYTE]))
    cg.add(var.set_photocell_mask(config[CONF_PHOTOCELL_MASK]))
    cg.add(var.set_io_poll_interval(config[CONF_IO_POLL_INTERVAL]))
    cg.add(var.set_io_poll_interval_closed(config[CONF_IO_POLL_INTERVAL_CLOSED]))
    cg.add(var.set_io_poll_while_moving(config[CONF_IO_POLL_WHILE_MOVING]))
    if CONF_PHOTOCELL in config:
        sens = await binary_sensor.new_binary_sensor(config[CONF_PHOTOCELL])
        cg.add(var.set_photocell_sensor(sens))

    cg.add(var.set_auto_close_register(config[CONF_AUTO_CLOSE_REGISTER]))
    cg.add(var.set_photo_close_register(config[CONF_PHOTO_CLOSE_REGISTER]))
    cg.add(var.set_config_readback_interval(config[CONF_CONFIG_READBACK_INTERVAL]))
    if CONF_AUTO_CLOSE_STATE in config:
        sens = await binary_sensor.new_binary_sensor(config[CONF_AUTO_CLOSE_STATE])
        cg.add(var.set_auto_close_state_sensor(sens))
    if CONF_PHOTO_CLOSE_STATE in config:
        sens = await binary_sensor.new_binary_sensor(config[CONF_PHOTO_CLOSE_STATE])
        cg.add(var.set_photo_close_state_sensor(sens))
