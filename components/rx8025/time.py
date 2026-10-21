import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, time
from esphome.const import CONF_ID

DEPENDENCIES = ["i2c"]

rx8025_ns = cg.esphome_ns.namespace("rx8025")
RX8025Component = rx8025_ns.class_("RX8025Component", time.RealTimeClock, i2c.I2CDevice)

CONFIG_SCHEMA = time.TIME_SCHEMA.extend(
    {cv.GenerateID(): cv.declare_id(RX8025Component)}
).extend(i2c.i2c_device_schema(0x32))


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)
    await time.register_time(var, config)
