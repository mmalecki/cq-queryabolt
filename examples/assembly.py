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

c_d = 10
c_h = 10

# This function returns a rectangle on the current workplane, optionally tagging it.
# This rectangle is later used to construct a mouting interface.
def m(workplane, tag=None):
    ret = workplane.rect(10, 10, forConstruction = True)
    if tag is not None:
        ret.tag(tag)
    return ret.vertices()

# Part A
a = Workplane().box(a_a, a_b, a_h)

# Create nutcatches on the "bottom" of the part.
a = m(a.faces("<Z").workplane()).nutcatchParallel("M3")
# And holes leading to them. Tag the rectangle we use for constructing the mounting
# as a mating face.
a = m(a.faces(">Z").workplane(), "mate_b").hole(3)

# Part B
b = Workplane().box(b_a, b_b, b_h)

# Grab the <Y face of the part, tag it as the part mating with C. Create a workplane
# 10 mm underneath, tag it as the workplane we'll be mounting C on.
# The 10 mm would usually be driven by design requirements.
b.faces("<Y").tag("mate_c").workplane(-10).tag("mount_c").end()
m(b.faces(">Z").workplane(), "mate_a")
b = m(b.faces("<Z").workplane().center(0, -10)).cboreHole(3, 6, 5)

# Sidecut nutcatches can be rotated if desired:
b = b.workplaneFromTagged("mount_c").transformed((0, 0, 180)).nutcatchSidecut("M4")
b = b.faces("<Y").hole(4, depth = 10)

# Part C
c = Workplane().circle(c_d).extrude(c_h)
c = c.faces(">Z").workplane().cboreHole(4, 8, 5)
c.faces("<Z").tag("mate_b").end()

assy = (cq.Assembly()
            .add(a, name = "a")
            .add(b, name = "b")
            .add(c, name = "c")

            .constrain("a?mate_b", "b?mate_a", "Point")
            .constrain("a@faces@>Z", "b@faces@>Z", "Axis")
            .constrain("a@edges@|Y", "b@edges@|Y", "Axis")

            .constrain("c?mate_b", "b?mate_c", "Plane")
)
assy.solve()

show_object(a.translate((a_a + 10, 0)), name="a", options=dict(alpha=0.3))
show_object(b.translate((2 * a_a + 20, 0, 0)), name="b", options=dict(alpha=0.3))
show_object(c.translate((2 * a_a + a_b + 30, 0, 0)), name="c", options=dict(alpha=0.3))
show_object(assy, name="assembly", options=dict(alpha=0.5))
