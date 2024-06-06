import app
from app_components import Menu, Notification, clear_background
import power

main_menu_items = [
    "Power",
]

power_menu_items = ["On", "Off"]


class BatteryMeter(app.App):
    def __init__(self):
        # Menu setup
        self.menu = None
        self.current_menu = None
        self.set_menu("main")

        # Notification setup
        self.notification = None

    def back_handler(self):
        # If in the topmost menu, minimize, otherwise move one menu up.
        if self.current_menu == "main":
            self.minimise()
        else:
            self.set_menu("main")

    def select_handler(self, item, idx):
        # If Power or Preset item selected enter that menu
        if item in main_menu_items:
            self.set_menu(item)
        else:
            if self.current_menu == "Power":
                if item == "On":
                    self.notification = Notification("Power On")
                    self.power = True
                    self.eye.value(0)
                    self.set_menu("main")
                elif item == "Off":
                    self.notification = Notification("Power Off")
                    self.power = False
                    self.dot1.value(1)
                    self.dot2.value(1)
                    self.dot3.value(1)
                    self.eye.value(1)
                    self.set_menu("main")
            else:
                self.notification = Notification(self.current_menu + "." + item + '"!')

    def set_menu(
        self,
        menu_name: Literal[
            "main",
            "Power",
        ],
    ):
        if self.menu:
            self.menu._cleanup()
        if self.current_menu:
            previous_menu = self.current_menu
        else:
            previous_menu = "Power"
        self.current_menu = menu_name
        if menu_name == "main":
            self.menu = Menu(
                self,
                main_menu_items,
                select_handler=self.select_handler,
                back_handler=self.back_handler,
                position=(main_menu_items).index(previous_menu),
            )
        elif menu_name == "Power":
            self.menu = Menu(
                self,
                power_menu_items,
                select_handler=self.select_handler,
                back_handler=self.back_handler,
                position=0 if self.power else 1,
            )

    def draw(self, ctx):

        BatteryChargeState = power.BatteryChargeState()
        BatteryLevel = power.BatteryLevel()
        Vbat = power.Vbat()
        Fault = power.Fault()
        SupplyCapabilities = power.SupplyCapabilities()[0]
        Icharge = power.Icharge()
        Vsys = power.Vsys()
        Vin = power.Vin()

        clear_background(ctx)

        self.menu.draw(ctx)

        if self.notification:
            self.notification.draw(ctx)

        batteryH = 120
        batteryW = 60
        batteryX = (batteryW / 2) * -1
        batteryY = 25

        clear_background(ctx)
        ctx.rgb(0, 0, 0)
        ctx.rectangle(-120, -120, 240, 240).fill()

        ctx.rgb(255, 255, 255)
        ctx.rectangle(-11, batteryY - batteryH - 11, 22, 12).fill()
        ctx.rectangle(
            batteryX - 1, batteryY + 1, batteryW + 2, (batteryH + 2) * -1
        ).fill()
        ctx.rgb(0, 0, 0)
        ctx.rectangle(-10, batteryY - batteryH - 10, 20, 10).fill()
        ctx.rectangle(batteryX, batteryY, batteryW, -batteryH).fill()

        r, g, b = get_color(BatteryLevel)
        ctx.rgb(r, g, b).rectangle(
            batteryX + 3,
            batteryY - 3,
            batteryW - 6,
            -(BatteryLevel / 100 * (batteryH - 6)),
        ).fill()
        ctx.rgb(r, g, b).move_to(0, 40).text("{:.1f}".format(BatteryLevel) + "%")

        ctx.rgb(255, 255, 255)
        ctx.move_to(1, 71).text(BatteryChargeState)
        ctx.move_to(0, 70).text(BatteryChargeState)
        if BatteryChargeState != "Not Charging":
            ctx.move_to(0, 90).text("{:.0f}".format(Icharge * 1000) + "ma")
            ctx.move_to(0, 110).text("{:.2f}".format(Vin) + "V")

        # ctx.rgb(255, 0, 0).move_to(0, -50).text(
        #     SupplyCapabilities[0]
        #     + " "
        #     + "{:.2f}".format(SupplyCapabilities[1])
        #     + " "
        #     + "{:.2f}".format(SupplyCapabilities[2])
        # )
        ctx.rgb(255, 255, 255).move_to(-69, -24).text("Bat")
        ctx.rgb(255, 255, 255).move_to(-70, -25).text("Bat")
        ctx.move_to(-70, 0).text("{:.2f}".format(Vbat) + "V")

        ctx.rgb(255, 255, 255).move_to(71, -24).text("Sys")
        ctx.rgb(255, 255, 255).move_to(70, -25).text("Sys")
        ctx.move_to(70, 0).text("{:.2f}".format(Vsys) + "V")

    def update(self, delta):
        self.menu.update(delta)
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
