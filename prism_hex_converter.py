import sys
from textwrap import wrap
from colorsys import rgb_to_hsv
colors = sys.argv[1:]
outstr = ""
try:
    for color in colors:
        rgb = [int(x,16)/255.0 for x in wrap(color,2)]
        hsv = rgb_to_hsv(*rgb)
        h = int(hsv[0] * 360)
        s = int(hsv[1] * 1000)
        v = int(hsv[2] * 1000)
        hsvb = "%0.4x%0.4x%0.4x00000000" % (h,s,v)
        outstr += hsvb
except Exception as e:
    print(e)
print(outstr)