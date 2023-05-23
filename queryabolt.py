import json
import math
import cadquery as cq

DEBUG = True

def dbg(r):
    if DEBUG:
        debug(r)
    return r

DEFAULT_NUT_KIND = "hexagon"

with open('nuts.json') as file:
  nuts = json.load(file)

def _hex_inscribed_circle_d (w):
    return 2 * w / math.sqrt(3)

def nut_data(options = None, kind = DEFAULT_NUT_KIND):
    if options is None:
        return nuts
    if isinstance(options, str):
        return nuts[options][kind]
    else:
        return options

def _nut_sketch(options, kind = DEFAULT_NUT_KIND):
    data = nut_data(options, kind)
    return (cq.Sketch()
                .regularPolygon(_hex_inscribed_circle_d(data["width"]) / 2, 6)
    )

def _nut_side_sketch(options, length, kind = DEFAULT_NUT_KIND):
    data = nut_data(options, kind)
    w = data["width"]
    e = -w * math.sqrt(3) / 6
    s = (cq.Sketch()
            .polygon([(-w / 2, length), (-w / 2, e), (0, -_hex_inscribed_circle_d(w) / 2), (w / 2, e), (w / 2, length)])
            .clean()
    )
    return s

class WorkplaneMixin:
    def nutcatchParallel(self, options, kind = DEFAULT_NUT_KIND, height_clearance = 0):
        data = nut_data(options, kind)
        return self.placeSketch(_nut_sketch(data)).cutBlind(-data["thickness"])

    def nutcatchSidecut(self, options, kind = DEFAULT_NUT_KIND, height_clearance = 0):
        data = nut_data(options, kind)
        l = self.largestDimension()
        return (self
                    .placeSketch(_nut_side_sketch(data, l))
                    .cutBlind(data["thickness"] + height_clearance)
        )

class Workplane(WorkplaneMixin, cq.Workplane):
    pass

a_a = 25
a_b = 25
a_h = 25

b_a = 22.5
b_b = 50
b_h = 10

def m(workplane, tag=None):
    ret = workplane.rect(10, 10, forConstruction = True)
    if tag is not None:
        ret.tag(tag)
    return ret.vertices()

a = Workplane().box(a_a, a_b, a_h)

a = m(a.faces("<Z").workplane()).nutcatchParallel("M3")
a = m(a.faces(">Z").workplane(), "mate").hole(3)

b = Workplane(origin=(a_a + 10, 0, 0)).box(b_a, b_b, b_h)

b.faces("<Y").workplane().tag("mate_c")
b = m(b.faces("<Z").workplane().center(0, -10)).cboreHole(3, 6, 5)
m(b.faces(">Z").workplane(), "mate")

# Without the `transformed`, this part would be unprintable:
b = b.workplaneFromTagged("mate_c").transformed((0, 0, 180)).workplane(-10).nutcatchSidecut("M4")

n = Workplane().box(a_a, a_b, a_h)
n = n.faces(">Z").workplane().pushPoints([(5, 0), (-5, 0)]).cboreHole(3, 6, 5)
n = n.faces("<Z").workplane(-2).pushPoints([(5, 0), (-5, 0)]).nutcatchSidecut("M3")

assy = (cq.Assembly()
            .add(a, name = "a")
            .add(b, name = "b")
            .constrain("a?mate", "b?mate", "Point")
            .constrain("a@faces@>Z", "b@faces@>Z", "Axis")
            .constrain("a@edges@|Y", "b@edges@|Y", "Axis")
)
assy.solve()

show_object(a, name="a", options=dict(alpha=0.3))
show_object(b, name="b", options=dict(alpha=0.3))
show_object(n.translate((a_a + a_b + 20, 0, 0)), name="nut", options=dict(alpha=0.0))
show_object(assy, name="assembly", options=dict(alpha=0.5))
