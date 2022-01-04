from os import getenv
from time import sleep
from PIL import Image
from dotenv import load_dotenv

from modules.time import draw_time
from modules.github import draw_github_contribution
import modules.pixoo_client as pixc

load_dotenv("local.env", verbose=True)

if __name__ == "__main__":
    bt_mac_addr = getenv("BT_MAC_ADDR")
    assert bt_mac_addr is not None, "Did you copy the example.env to local.env?"

    print(bt_mac_addr)
    pixoo = pixc.PixooMax(bt_mac_addr)
    pixoo.connect()

    while True:  # Main loop - here you can change the drawing functions
        base = Image.new("RGBA", (32, 32), (0, 0, 0, 0))  # Create a base new image
        time_img = draw_time(x_max=32, y_max=32)  # Draw the clock
        base.alpha_composite(time_img)  # Add the clock to the base image

        # this draws the github contribution pixel on top of the base image
        draw_github_contribution(base, "HoroTW", required_contributions=1)

        # workaround for final displaying
        base.save("tmp.png")
        pixoo.draw_pic("tmp.png")
        sleep(1.0 / 10)  # 10 fps are already pretty smooth
