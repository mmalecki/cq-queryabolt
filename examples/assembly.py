import queryabolt
import cadquery as cq

class Workplane(queryabolt.WorkplaneMixin, cq.Workplane):
    pass

DEBUG = True

def dbg(r):
    if DEBUG:
        debug(r)
    return r

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
