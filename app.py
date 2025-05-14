import app
from app_components import Menu, Notification, clear_background
import power
from events.input import Button, BUTTON_TYPES, ButtonDownEvent, ButtonUpEvent
from system.eventbus import eventbus
from system.scheduler.events import RequestForegroundPushEvent


class BatteryMeter(app.App):
    def __init__(self):

        self.app = app

        # Notification setup
        self.notification = None

        # App setup
        self.chargingCounter = 0

        # Button setup
        eventbus.on(ButtonDownEvent, self._handle_buttondown, self)

        eventbus.on(
            RequestForegroundPushEvent, self._handle_request_foreground_push, self
        )

        # Page setup
        self.page = "main"

        # Constants for battery dimensions
        self.BATTERY_HEIGHT = 120
        self.BATTERY_WIDTH = 60
        self.BATTERY_X = (self.BATTERY_WIDTH / 2) * -1
        self.BATTERY_Y = 20

    def _handle_request_foreground_push(self, event: RequestForegroundPushEvent):
        eventbus.on(ButtonDownEvent, self._handle_buttondown, self)

    def _cleanup(self):
        eventbus.remove(ButtonDownEvent, self._handle_buttondown, self.app)

    def draw(self, ctx):

        if self.notification:
            self.notification.draw(ctx)

        clear_background(ctx)

        if self.page == "main":
            BatteryChargeState = power.BatteryChargeState()
            BatteryLevel = max(0, min(100, power.BatteryLevel()))  # Clamp to [0, 100]
            Vbat, Icharge, Vsys, Vin = (
                power.Vbat(),
                power.Icharge(),
                power.Vsys(),
                power.Vin(),
            )

            BatteryChargeState = (
                "Finished Charging"
                if BatteryChargeState == "Terminated"
                else BatteryChargeState
            )

            ctx.font_size = 22
            ctx.text_align = ctx.CENTER
            ctx.rgb(0, 0, 0)
            ctx.rectangle(-120, -120, 240, 240).fill()

            # Draw battery outline
            ctx.rgb(255, 255, 255)
            ctx.rectangle(-11, self.BATTERY_Y - self.BATTERY_HEIGHT - 11, 22, 12).fill()
            ctx.rectangle(
                self.BATTERY_X - 1,
                self.BATTERY_Y + 1,
                self.BATTERY_WIDTH + 2,
                (self.BATTERY_HEIGHT + 2) * -1,
            ).fill()
            ctx.rgb(0, 0, 0)
            ctx.rectangle(-10, self.BATTERY_Y - self.BATTERY_HEIGHT - 10, 20, 10).fill()
            ctx.rectangle(
                self.BATTERY_X, self.BATTERY_Y, self.BATTERY_WIDTH, -self.BATTERY_HEIGHT
            ).fill()

            # Draw battery level
            r, g, b = get_color(BatteryLevel)
            ctx.rgb(r, g, b).rectangle(
                self.BATTERY_X + 3,
                self.BATTERY_Y - 3,
                self.BATTERY_WIDTH - 6,
                -(BatteryLevel / 100 * (self.BATTERY_HEIGHT - 6)),
            ).fill()

            ctx.rgb(r, g, b).move_to(0, 38).text("{:.1f}".format(BatteryLevel) + "%")

            # Charging animation
            if BatteryChargeState == "Fast Charging":
                self.chargingCounter += Icharge * 10 / 3
                ChargingBatteryLevel = min(100, BatteryLevel + self.chargingCounter)
                r2, g2, b2 = get_color(ChargingBatteryLevel)
                ctx.rgb(r2, g2, b2).rectangle(
                    self.BATTERY_X + 3,
                    self.BATTERY_Y
                    - 3
                    - (BatteryLevel / 100 * (self.BATTERY_HEIGHT - 6))
                    - 1,
                    self.BATTERY_WIDTH - 6,
                    -(ChargingBatteryLevel / 100 * (self.BATTERY_HEIGHT - 6))
                    + (BatteryLevel / 100 * (self.BATTERY_HEIGHT - 6))
                    + 2,
                ).fill()

                if ChargingBatteryLevel >= 100:
                    self.chargingCounter = 0
            else:
                self.chargingCounter = 0

            # Display battery info
            ctx.rgb(255, 255, 255)
            ctx.move_to(0, 63).text(BatteryChargeState)
            if BatteryChargeState != "Not Charging":
                ctx.move_to(0, 85).text(f"{Icharge * 1000:.0f}ma")
                ctx.move_to(0, 105).text(f"{Vin:.2f}V")

            # Display voltage info
            ctx.rgb(255, 255, 255).move_to(-69, -24).text("Bat")
            ctx.rgb(255, 255, 255).move_to(-70, -25).text("Bat")
            ctx.move_to(-70, 0).text(f"{Vbat:.2f}V")

            ctx.rgb(255, 255, 255).move_to(71, -24).text("Sys")
            ctx.rgb(255, 255, 255).move_to(70, -25).text("Sys")
            ctx.move_to(70, 0).text(f"{Vsys:.2f}V")

        elif self.page == "info":

            ctx.text_align = ctx.CENTER
            ctx.rgb(0, 0, 0)
            ctx.rectangle(-120, -120, 240, 240).fill()

            ctx.rgb(255, 255, 255)
            ctx.font_size = 35
            ctx.rgb(255, 255, 255).move_to(0, -90).text("Info")

            # Charger
            SupplyCapabilities = power.SupplyCapabilities()[0]

            ctx.font_size = 26
            ctx.move_to(0, -60).text("Charger")
            if SupplyCapabilities[0] != "disconnected":
                ctx.font_size = 22
                ctx.move_to(0, -40).text("Capabilities: " + str(SupplyCapabilities[0]))
                ctx.move_to(0, -20).text(
                    "Current: {:.0f}".format(SupplyCapabilities[1]) + "ma"
                )
                ctx.move_to(0, 0).text(
                    "Voltage: {:.2f}".format(SupplyCapabilities[2]) + "V"
                )
            else:
                ctx.font_size = 22
                ctx.move_to(0, -40).text("Disconnected")

            # Status
            Fault = power.Fault()

            ctx.font_size = 26
            ctx.move_to(0, 35).text("Status")

            ctx.font_size = 22
            currentY = 55
            for key, value in Fault.items():
                ctx.move_to(0, currentY).text(key + ": " + str(value))
                currentY += 20

    def _handle_buttondown(self, event: ButtonDownEvent):
        if BUTTON_TYPES["CANCEL"] in event.button:
            if self.page == "main":
                self._cleanup()
                self.minimise()
            else:
                self.page = "main"

        if BUTTON_TYPES["CONFIRM"] in event.button:
            if self.page == "main":
                self.page = "info"

    def update(self, delta):

        if self.notification:
            self.notification.update(delta)


def get_color(battery_percentage):
    hue = 120 * (battery_percentage / 100)
    r, g, b = hsv_to_rgb(hue / 360, 1, 1)
    return (r / 255), (g / 255), (b / 255)


def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return (v, v, v)
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = int(v * (1.0 - s) * 255)
    q = int(v * (1.0 - s * f) * 255)
    t = int(v * (1.0 - s * (1.0 - f)) * 255)
    v = int(v * 255)
    i %= 6
    if i == 0:
        return (v, t, p)
    if i == 1:
        return (q, v, p)
    if i == 2:
        return (p, v, t)
    if i == 3:
        return (p, q, v)
    if i == 4:
        return (t, p, v)
    if i == 5:
        return (v, p, q)


__app_export__ = BatteryMeter
