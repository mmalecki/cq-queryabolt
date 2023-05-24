import json
import math
import pathlib
import cadquery as cq

DEFAULT_HEAD_DIAMETER_CLEARANCE = 0.1
DEFAULT_NUT_KIND = "hexagon"
DEFAULT_BOLT_KIND = "headless"

_dataDir = pathlib.Path(__file__).parent.resolve()

with open(pathlib.PurePath(_dataDir, 'nuts.json')) as file:
  nuts = json.load(file)

with open(pathlib.PurePath(_dataDir, 'bolts.json')) as file:
  bolts = json.load(file)

def _hexInscribedCircle (w):
    return 2 * w / math.sqrt(3)

def _nutSketch(options, kind = DEFAULT_NUT_KIND):
    data = nutData(options, kind)
    return (cq.Sketch()
                .regularPolygon(_hexInscribedCircle(data["width"]) / 2, 6)
    )

def _nutSideSketch(options, length, kind = DEFAULT_NUT_KIND):
    data = nutData(options, kind)
    w = data["width"]
    e = -w * math.sqrt(3) / 6
    s = (cq.Sketch()
            .polygon([(-w / 2, length), (-w / 2, e), (0, -_hexInscribedCircle(w) / 2), (w / 2, e), (w / 2, length)])
            .clean()
    )
    return s

def nutData(options = None, kind = DEFAULT_NUT_KIND):
    if options is None:
        return nuts
    if isinstance(options, str):
        return nuts[options][kind]
    else:
        return options

def boltData(options = None, kind = DEFAULT_BOLT_KIND):
    if options is None:
        return bolts
    if isinstance(options, str):
        return bolts[options][kind]
    else:
        return options

class WorkplaneMixin:
    def nutcatchParallel(self, options, kind = DEFAULT_NUT_KIND, heightClearance = 0):
        data = nutData(options, kind)
        return self.placeSketch(_nutSketch(data)).cutBlind(-(data["thickness"] + heightClearance))

    def nutcatchSidecut(self, options, kind = DEFAULT_NUT_KIND, heightClearance = 0, length = None):
        data = nutData(options, kind)

        if length is None:
            length = self.largestDimension()

        return (self
                    .placeSketch(_nutSideSketch(data, length))
                    .cutBlind(data["thickness"] + heightClearance)
        )

    def boltHole(self, bolt, depth = None):
        data = boltData(bolt)
        return self.hole(data["diameter"], depth)

    def cboreBoltHole(self, bolt, depth = None, headDiameterClearance = DEFAULT_HEAD_DIAMETER_CLEARANCE):
        data = boltData(bolt, "socket_head")
        cboreD = data["head_diameter"] + headDiameterClearance
        return self.cboreHole(data["diameter"], cboreD, cboreDepth = data["head_length"], depth = depth)

    def cskBoltHole(self, bolt, depth = None):
        data = boltData(bolt, "countersunk")
        return self.cskHole(data["diameter"], data["head_diameter"], cskAngle = 90, depth = depth)
