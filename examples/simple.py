import queryabolt
import cadquery as cq

class Workplane(queryabolt.WorkplaneMixin, cq.Workplane):
    pass

a = 50
b = 25
h = 25
nutcatchSideOffset = 7.5

box = Workplane().box(a, b, h)

box.faces(">X").workplane().tag("side").end()

# A lock nutcatch on the bottom:
result = box.faces("<Z").workplane().tag("center").nutcatchParallel("M3", "hexagon_lock")
result = result.faces(">Z").workplane().boltHole("M3")

# Get one on the top as well:
result = result.faces(">Z").workplane().center(0, -b / 4).nutcatchParallel("M3")
result = result.faces("<Z").workplane().boltHole("M3")

# An M5 nutcatch with a countersunk screw:
result = result.faces("<Z").workplane().center(10, 0).nutcatchParallel("M5")
result = result.faces(">Z").workplane().cskBoltHole("M5")
# And just a countersunk M5 with a countersunk screw: TODO: countersink this a head's length
result = result.faces("<Z").workplane().center(0, -b / 2).nutcatchParallel("M5")
result = result.faces(">Z").workplane().cskBoltHole("M5")

# An M8 nutcatch with a socket head countersunk screw:
result = result.faces("<Z").workplaneFromTagged("center").center(-15, 0).nutcatchParallel("M8")
result = result.faces(">Z").workplane().cboreBoltHole("M8") # TODO: only cbore a half head

# A sidecut nutcatch:
# A sidecut locknut catch:
result = result.workplaneFromTagged("side").workplane(-nutcatchSideOffset).center(-5, -h / 2 + 4)
result = result.nutcatchSidecut("M3", kind = "hexagon_lock")
result = result.center(10, 0).nutcatchSidecut("M3")

result = result.workplaneFromTagged("side").center(-5, -h / 2 + 4).boltHole("M3", depth = nutcatchSideOffset)
result = result.center(10, 0).boltHole("M3", depth = nutcatchSideOffset)

show_object(result, name="simple", options=dict(alpha=0.3))
