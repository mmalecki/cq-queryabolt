import json
import math
import pathlib
import cadquery as cq

DEFAULT_NUT_KIND = "hexagon"

_dataDir = pathlib.Path(__file__).parent.resolve()

with open(pathlib.PurePath(_dataDir, 'nuts.json')) as file:
  nuts = json.load(file)

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

class WorkplaneMixin:
    def nutcatchParallel(self, options, kind = DEFAULT_NUT_KIND, height_clearance = 0):
        data = nutData(options, kind)
        return self.placeSketch(_nutSketch(data)).cutBlind(-data["thickness"])

    def nutcatchSidecut(self, options, kind = DEFAULT_NUT_KIND, height_clearance = 0):
        data = nutData(options, kind)
        l = self.largestDimension()
        return (self
                    .placeSketch(_nutSideSketch(data, l))
                    .cutBlind(data["thickness"] + height_clearance)
        )
