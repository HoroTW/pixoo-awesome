from PIL import Image, ImageDraw

DEBUG = False
x_size = 32
y_size = 32
x_middle = x_size / 2
y_middle = y_size / 2
short_line = x_size / 10
bgcolor = (120, 120, 120, 255)
fgcolor1 = (255, 90, 255, 255)  # red
fgcolor2 = (90, 255, 90, 255)  # green
fgcolor3 = (90, 90, 255, 255)  # blue


def __draw_time(x_max=31, y_max=31):
    from datetime import datetime
    # get current time seconds
    now = datetime.now()
    # get milliseconds
    curMinutes = now.minute
    curHours = now.hour
    curSeconds = now.second
    curMs = now.microsecond / 1000
    mul = 4

    if DEBUG:
        curMinutes = 0
        curHours = 8.88
        curSeconds = 30
        curMs = 0

    middle_point = (x_max / 2 * mul, y_max / 2 * mul)
    sec_hand_len_percent = 0.85
    min_hand_len_percent = 0.71
    hour_hand_len_percent = 0.45

    x_middle = x_max / 2 * mul
    y_middle = y_max / 2 * mul
    sec_top_point = (middle_point[0],
                     x_middle - x_middle * sec_hand_len_percent)
    min_top_point = (middle_point[0],
                     x_middle - x_middle * min_hand_len_percent)
    hour_top_point = (middle_point[0],
                      x_middle - x_middle * hour_hand_len_percent)

    out = Image.new("RGBA", (x_size, y_size), (255, 255, 255, 0))
    time_sec = Image.new("RGBA", (x_size * mul, y_size * mul),
                         (255, 255, 255, 0))
    time_min = Image.new("RGBA", (x_size * mul, y_size * mul),
                         (255, 255, 255, 0))
    time_hour = Image.new("RGBA", (x_size * mul, y_size * mul),
                          (255, 255, 255, 0))
    center_dot = Image.new("RGBA", (x_size * mul, y_size * mul),
                           (255, 255, 255, 0))
    frame = Image.new("RGBA", (x_size * mul, y_size * mul), (255, 255, 255, 0))
    face = Image.new("RGBA", (x_size * mul, y_size * mul), (255, 255, 255, 0))

    # rotate_angle = curHours*(360/12)
    rotate_angle = curHours * (360 / 12) + curMinutes * (360 / (12 * 60))
    time_hour = time_hour.rotate(rotate_angle, center=middle_point)
    ImageDraw.Draw(time_hour).line(
        (middle_point, hour_top_point),
        fill=fgcolor3,
        width=2 * mul,
    )  # hour
    time_hour = time_hour.rotate(-rotate_angle, center=middle_point)

    # rotate_angle = curMinutes*(360/60)
    rotate_angle = curMinutes * (360 / 60) + curSeconds * (360 / (60 * 60))
    time_min = time_min.rotate(rotate_angle, center=middle_point)
    ImageDraw.Draw(time_min).line((middle_point, min_top_point),
                                  fill=fgcolor2,
                                  width=1 * mul)  # minute
    time_min = time_min.rotate(-rotate_angle, center=middle_point)

    # rotate_angle = curSeconds*(360/60)
    rotate_angle = curSeconds * (360 / 60) + curMs * (360 / (60 * 1000))
    time_sec = time_sec.rotate(rotate_angle, center=middle_point)
    ImageDraw.Draw(time_sec).line((middle_point, sec_top_point),
                                  fill=fgcolor1,
                                  width=1 * mul)  # second
    time_sec = time_sec.rotate(-rotate_angle, center=middle_point)

    # center dot
    center_dot_tl = (x_middle - 1.5 * mul, y_middle - 1.5 * mul)
    center_dot_br = (x_middle + 1.5 * mul, y_middle + 1.5 * mul)
    ImageDraw.Draw(center_dot).rounded_rectangle(
        (*center_dot_tl, *center_dot_br),
        radius=1.5 * mul,
        fill=(80, 80, 80, 255))

    # frame
    ImageDraw.Draw(frame).rounded_rectangle((0, 0, x_max * mul, y_max * mul),
                                            outline=bgcolor,
                                            radius=13 * mul,
                                            width=1 * mul)

    # face
    ImageDraw.Draw(face).line(((x_middle, 0), (x_middle, 3.2 * mul)),
                              fill=bgcolor,
                              width=1 * mul)
    face.alpha_composite(face.copy().rotate(180, center=middle_point))
    face.alpha_composite(face.copy().rotate(90, center=middle_point))
    temp = face.copy()
    face.alpha_composite(temp.copy().rotate(30, center=middle_point))
    face.alpha_composite(temp.copy().rotate(-30, center=middle_point))

    # merge images
    out = Image.alpha_composite(out,
                                face.resize((x_size, y_size), Image.LANCZOS))
    out = Image.alpha_composite(
        out, time_hour.resize((x_size, y_size), Image.LANCZOS))
    out = Image.alpha_composite(
        out, time_min.resize((x_size, y_size), Image.LANCZOS))
    out = Image.alpha_composite(
        out, time_sec.resize((x_size, y_size), Image.LANCZOS))
    out = Image.alpha_composite(
        out, center_dot.resize((x_size, y_size), Image.NEAREST))
    out = Image.alpha_composite(out,
                                frame.resize((x_size, y_size), Image.LANCZOS))

    if DEBUG:
        __draw_debug_points(out, x_max, y_max)

    return out


def __draw_hour_indicators():
    out = Image.new("RGBA", (x_size, y_size), (0, 0, 0, 0))
    ImageDraw.Draw(out).line(((x_middle, 0), (x_middle, short_line)),
                             fill=bgcolor,
                             width=1)

    out.alpha_composite(out.copy().rotate(180))
    out.alpha_composite(out.copy().rotate(90))
    temp = out.copy()

    out.alpha_composite(temp.copy().rotate(30))
    out.alpha_composite(temp.copy().rotate(-30))

    return out


def __draw_debug_points(base, x_max=31, y_max=31):
    x_max, y_max = x_max - 1, y_max - 1
    x_mid, y_mid = x_max / 2, y_max / 2

    points = [(x_mid, y_mid), (x_mid, y_max), (x_max, y_mid), (x_mid, 0),
              (0, y_mid), (0, 0), (x_max, y_max), (x_max, 0), (0, y_max)]

    [
        ImageDraw.Draw(base).point(point, fill=(255, 0, 0, 255))
        for point in points
    ]


def draw_time(x_max=21, y_max=21) -> Image:
    base = Image.new('RGBA', (32, 32), (0, 0, 0))
    time = __draw_time(x_max, y_max)
    base.alpha_composite(time)
    return base
