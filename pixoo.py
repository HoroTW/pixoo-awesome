"""
Pixoo 
"""
# %%

import socket
from time import sleep
from PIL import Image, ImageDraw
from math import log10, ceil

class Pixoo(object):

  CMD_SET_SYSTEM_BRIGHTNESS = 0x74
  CMD_SPP_SET_USER_GIF = 0xb1
  CMD_DRAWING_ENCODE_PIC = 0x5b

  BOX_MODE_CLOCK=0
  BOX_MODE_TEMP=1
  BOX_MODE_COLOR=2
  BOX_MODE_SPECIAL=3

  instance = None

  def __init__(self, mac_address):
    """
    Constructor
    """
    self.mac_address = mac_address
    self.btsock = None


  @staticmethod
  def get():
    if Pixoo.instance is None:
      Pixoo.instance = Pixoo(Pixoo.BDADDR)
      Pixoo.instance.connect()
    return Pixoo.instance

  def connect(self):
    """
    Connect to SPP.
    """
    self.btsock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    self.btsock.connect((self.mac_address, 1))


  def __spp_frame_checksum(self, args):
    """
    Compute frame checksum
    """
    return sum(args[1:])&0xffff


  def __spp_frame_encode(self, cmd, args):
    """
    Encode frame for given command and arguments (list).
    """
    payload_size = len(args) + 3

    # create our header
    frame_header = [1, payload_size & 0xff, (payload_size >> 8) & 0xff, cmd]

    # concatenate our args (byte array)
    frame_buffer = frame_header + args

    # compute checksum (first byte excluded)
    cs = self.__spp_frame_checksum(frame_buffer)

    # create our suffix (including checksum)
    frame_suffix = [cs&0xff, (cs>>8)&0xff, 2]

    # return output buffer
    return frame_buffer+frame_suffix


  def send(self, cmd, args):
    """
    Send data to SPP.
    """
    spp_frame = self.__spp_frame_encode(cmd, args)
    if self.btsock is not None:
      nb_sent = self.btsock.send(bytes(spp_frame))


  def set_system_brightness(self, brightness):
    """
    Set system brightness.
    """
    self.send(Pixoo.CMD_SET_SYSTEM_BRIGHTNESS, [brightness&0xff])


  def set_box_mode(self, boxmode, visual=0, mode=0):
    """
    Set box mode.
    """
    self.send(0x45, [boxmode&0xff, visual&0xff, mode&0xff])


  def set_color(self, r,g,b):
    """
    Set color.
    """
    self.send(0x6f, [r&0xff, g&0xff, b&0xff])

  def encode_image(self, filepath):
    img = Image.open(filepath)
    return self.encode_raw_image(img)

  def encode_raw_image(self, img):
    """
    Encode a 16x16 image.
    """
    # ensure image is 16x16
    w,h = img.size
    if w == h:
      # resize if image is too big
      if w > 16:
        img = img.resize((16,16))

      # create palette and pixel array
      pixels = []
      palette = []
      for y in range(16):
        for x in range(16):
          pix = img.getpixel((x,y))
          
          if len(pix) == 4:
            r,g,b,a = pix
          elif len(pix) == 3:
            r,g,b = pix
          if (r,g,b) not in palette:
            palette.append((r,g,b))
            idx = len(palette)-1
          else:
            idx = palette.index((r,g,b))
          pixels.append(idx)

      # encode pixels
      bitwidth = ceil(log10(len(palette))/log10(2))
      nbytes = ceil((256*bitwidth)/8.)
      encoded_pixels = [0]*nbytes

      encoded_pixels = []
      encoded_byte = ''
      for i in pixels:
        encoded_byte = bin(i)[2:].rjust(bitwidth, '0') + encoded_byte
        if len(encoded_byte) >= 8:
            encoded_pixels.append(encoded_byte[-8:])
            encoded_byte = encoded_byte[:-8]
      encoded_data = [int(c, 2) for c in encoded_pixels]
      encoded_palette = []
      for r,g,b in palette:
        encoded_palette += [r,g,b]
      return (len(palette), encoded_palette, encoded_data)
    else:
      print('[!] Image must be square.')

  def draw_gif(self, filepath, speed=100):
    """
    Parse Gif file and draw as animation.
    """
    # encode frames
    frames = []
    timecode = 0
    anim_gif = Image.open(filepath)
    for n in range(anim_gif.n_frames):
      anim_gif.seek(n)
      nb_colors, palette, pixel_data = self.encode_raw_image(anim_gif.convert(mode='RGB'))
      frame_size = 7 + len(pixel_data) + len(palette)
      frame_header = [0xAA, frame_size&0xff, (frame_size>>8)&0xff, timecode&0xff, (timecode>>8)&0xff, 0, nb_colors]
      frame = frame_header + palette + pixel_data
      frames += frame
      timecode += speed

    # send animation
    nchunks = ceil(len(frames)/200.)
    total_size = len(frames)
    for i in range(nchunks):
      chunk = [total_size&0xff, (total_size>>8)&0xff, i]
      self.send(0x49, chunk+frames[i*200:(i+1)*200])
   

  def draw_anim(self, filepaths, speed=100):
    timecode=0

    # encode frames
    frames = []
    n=0
    for filepath in filepaths:
      nb_colors, palette, pixel_data = self.encode_image(filepath)
      frame_size = 7 + len(pixel_data) + len(palette)
      frame_header = [0xAA, frame_size&0xff, (frame_size>>8)&0xff, timecode&0xff, (timecode>>8)&0xff, 0, nb_colors]
      frame = frame_header + palette + pixel_data
      frames += frame
      timecode += speed
      n += 1
    
    # send animation
    nchunks = ceil(len(frames)/200.)
    total_size = len(frames)
    for i in range(nchunks):
      chunk = [total_size&0xff, (total_size>>8)&0xff, i]
      self.send(0x49, chunk+frames[i*200:(i+1)*200])


  def draw_pic(self, filepath):
    """
    Draw encoded picture.
    """
    nb_colors, palette, pixel_data = self.encode_image(filepath)
    frame_size = 7 + len(pixel_data) + len(palette)
    frame_header = [0xAA, frame_size&0xff, (frame_size>>8)&0xff, 0, 0, 0, nb_colors]
    frame = frame_header + palette + pixel_data
    prefix = [0x0, 0x0A,0x0A,0x04]
    self.send(0x44, prefix+frame)


class PixooMax(Pixoo):
  """
  PixooMax class, derives from Pixoo but does not support animation yet.
  """
  
  def __init__(self, mac_address):
    super().__init__(mac_address)

  def draw_pic(self, filepath):
    """
    Draw encoded picture.
    """
    nb_colors, palette, pixel_data = self.encode_image(filepath)
    frame_size = 8 + len(pixel_data) + len(palette)
    frame_header = [0xAA, frame_size&0xff, (frame_size>>8)&0xff, 0, 0, 3, nb_colors&0xff, (nb_colors&0xff00)>>8]
    frame = frame_header + palette + pixel_data
    prefix = [0x0, 0x0A,0x0A,0x04]
    self.send(0x44, prefix+frame)

  def draw_gif(self, filepath, speed=100):
    raise 'NotYetImplemented'

  def draw_anim(self, filepaths, speed=100):
    raise 'NotYetImplemented'

  def encode_image(self, filepath):
    img = Image.open(filepath)
    return self.encode_raw_image(img)

  def encode_raw_image(self, img):
    """
    Encode a 32x32 image.
    """
    # ensure image is 32x32
    w,h = img.size
    if w == h:
      # resize if image is too big
      if w > 32:
        img = img.resize((32,32))

      # ensure a maximum of 256 colors
      img = img.convert(mode="P", palette=Image.ADAPTIVE, colors=256).convert(mode="RGB")

      # create palette and pixel array
      pixels = []
      palette = []
      for y in range(32):
        for x in range(32):
          pix = img.getpixel((x,y))
          
          if len(pix) == 4:
            r,g,b,a = pix
          elif len(pix) == 3:
            r,g,b = pix
          if (r,g,b) not in palette:
            palette.append((r,g,b))
            idx = len(palette)-1
          else:
            idx = palette.index((r,g,b))
          pixels.append(idx)

      # encode pixels
      bitwidth = ceil(log10(len(palette))/log10(2))
      nbytes = ceil((256*bitwidth)/8.)
      encoded_pixels = [0]*nbytes

      encoded_pixels = []
      encoded_byte = ''
      for i in pixels:
        encoded_byte = bin(i)[2:].rjust(bitwidth, '0') + encoded_byte
        if len(encoded_byte) >= 8:
            encoded_pixels.append(encoded_byte[-8:])
            encoded_byte = encoded_byte[:-8]
      encoded_data = [int(c, 2) for c in encoded_pixels]
      encoded_palette = []
      for r,g,b in palette:
        encoded_palette += [r,g,b]
      return (len(palette), encoded_palette, encoded_data)
    else:
      print('[!] Image must be square.')

if __name__ == '__main__':
    pass


pixoo = PixooMax("11:75:58:F0:DE:D6")
pixoo.connect()
# mandatory to wait at least 1 second
sleep(1)


# %% Start of some Animation examples
# setting some variables
x_size = 32
y_size = 32
x_middle = x_size/2
y_middle = y_size/2
short_line = x_size/10
bgcolor = (120,120,120,255)
fgcolor1 = (255,90,255,255) # red
fgcolor2 = (90,255,90,255)  # green
fgcolor3 = (90,90,255,255)  # blue

def draw_animation(base: Image.Image, step=1):
    return ImageDraw.Draw(base.copy()).rounded_rectangle(
        (0 + step, 0 + step, (x_size - 1) - step, (x_size - 1) - step),
        outline=bgcolor,
        radius=3,
    )

# create a new image, RGB mode
base = Image.new('RGBA', (32,32), (0,0,0))

# %%
for i in range(5):
  for j in range(16):
    layer = draw_animation(j)
    out = Image.alpha_composite(base, layer)
    out.save('/tmp/test.png')
    pixoo.draw_pic('/tmp/test.png')
    sleep(1.0/30)

  for j in range(15,-1,-1):
    layer = draw_animation(j)
    out = Image.alpha_composite(base, layer)
    out.save('/tmp/test.png')
    pixoo.draw_pic('/tmp/test.png')
    sleep(1.0/30)

layer = draw_animation(1,False)
out = Image.alpha_composite(base, layer)
out.save('/tmp/test.png')
pixoo.draw_pic('/tmp/test.png')

# %%
def draw_time():
  from datetime import datetime
  # get current time seconds
  now = datetime.now()
  # get milliseconds
  curMinutes = now.minute
  curHours = now.hour
  curSeconds = now.second
  curMs = now.microsecond/1000

  out = Image.new("RGBA", (32,32), (255, 255, 255, 0))
  time_sec = Image.new("RGBA", (32,32), (255, 255, 255, 0))
  time_min = Image.new("RGBA", (32,32), (255, 255, 255, 0))
  time_hour = Image.new("RGBA", (32,32), (255, 255, 255, 0))


  # rotate_angle = curHours*(360/12)
  rotate_angle = curHours*(360/12) + curMinutes*(360/(12*60))
  time_hour = time_hour.rotate( rotate_angle , )
  ImageDraw.Draw(time_hour).line(((15.5,15.5),(15.5,(15.5-7))), fill=fgcolor3, width=2) # hour
  time_hour = time_hour.rotate( -rotate_angle, )

  # rotate_angle = curMinutes*(360/60)
  rotate_angle = curMinutes*(360/60) + curSeconds*(360/(60*60))
  time_min = time_min.rotate( rotate_angle , )
  ImageDraw.Draw(time_min).line(((15.5,15.5),(15.5,(15.5-11))), fill=fgcolor2, width=1) # minute
  time_min = time_min.rotate( -rotate_angle , )

  # rotate_angle = curSeconds*(360/60)
  rotate_angle = curSeconds*(360/60) + curMs*(360/(60*1000))
  time_sec = time_sec.rotate( rotate_angle , )
  ImageDraw.Draw(time_sec).line(((15.5,15.5),(15.5,(15.5-13))), fill=fgcolor1, width=1) # second
  time_sec = time_sec.rotate( -rotate_angle )

  # merge images
  out = Image.alpha_composite(out, time_hour.resize((128,128)).resize((32,32), Image.LANCZOS))
  out = Image.alpha_composite(out, time_min.resize((128,128)).resize((32,32), Image.LANCZOS))
  out = Image.alpha_composite(out, time_sec.resize((128,128)).resize((32,32), Image.LANCZOS))


  ImageDraw.Draw(out).rounded_rectangle((15,15,16,16),radius=2, fill=(255,255,255,80))

  return out




def draw_hour_indicators():
  out = Image.new("RGBA", (x_size, y_size), (0, 0, 0, 0))
  ImageDraw.Draw(out).line( ((x_middle, 0), (x_middle, short_line)), fill=bgcolor, width=1)

  out.alpha_composite(out.copy().rotate(180))
  out.alpha_composite(out.copy().rotate(90))
  temp = out.copy()

  out.alpha_composite(temp.copy().rotate(30))
  out.alpha_composite(temp.copy().rotate(-30))

  return out


while True:
  base = Image.new('RGBA', (32,32), (0,0,0))
  base.alpha_composite(draw_hour_indicators())
  clock_border_width = 1
  ImageDraw.Draw(base).rounded_rectangle((0 + clock_border_width, 0 + clock_border_width, 31 - clock_border_width, 31 - clock_border_width),outline=bgcolor, radius=3)
  base.alpha_composite(draw_animation(1,False))
  base.alpha_composite(draw_time())
  ImageDraw.Draw(base).rectangle((0,0,31,31), outline=(0,0,0,255))

  base.save('/tmpfs/test.png')
  pixoo.draw_pic('/tmpfs/test.png')
  sleep(1.0/5)
