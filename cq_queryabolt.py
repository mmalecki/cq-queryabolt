import json
import math
import pathlib
import cadquery as cq
from typing import Union, Optional

DEFAULT_CLEARANCE = 0.0
DEFAULT_HEAD_DIAMETER_CLEARANCE = 0.1
DEFAULT_NUT_KIND = "hexagon"
DEFAULT_BOLT_KIND = "headless"

"""Either a string describing a fastener (e.g. `"M3"`), or an object containing all
the necessary fastener properties."""
FastenerSpec = Union[str, object]

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
    """Mixin for cadquery.Workplane containing cq_queryabolt methods."""

    def nutcatchParallel(self, options: FastenerSpec, kind = DEFAULT_NUT_KIND, heightClearance = 0.0):
        """Make a parallel (surface) nutcatch

        Args:
            options (str): name of the nut (e.g. `"M3"`)
            kind (str, optional): kind of the nut (e.g. `"hexagon"`). Defaults to `"hexagon"`.
            heightClearance (float, optional): height clearance for the nut. Defaults to 0.
        """
        data = nutData(options, kind)
        return self.placeSketch(_nutSketch(data)).cutBlind(-(data["thickness"] + heightClearance))

    def nutcatchSidecut(self, options: FastenerSpec, kind = DEFAULT_NUT_KIND, heightClearance = 0.0, depth: Optional[float] = None):
        """Make a side-cut nutcatch

        Args:
            options (str): name of the nut (e.g. `"M3"`)
            kind (str, optional): kind of the nut (e.g. `"hexagon"`). Defaults to `"hexagon"`.
            heightClearance (float >= 0, optional): additional height clearance for the nut. Defaults to 0.
            depth (float > 0 or None to cut through the entire part): how deep to make the sidecut. Defaults to None.
        """
        data = nutData(options, kind)

        if depth is None:
            depth = self.largestDimension()

        return (self
                    .placeSketch(_nutSideSketch(data, depth))
                    .cutBlind(data["thickness"] + heightClearance)
        )

    def boltHole(self, bolt: FastenerSpec, depth: Optional[float] = None, clearance = DEFAULT_CLEARANCE):
        """Make a bolt hole (`cadquery.Workplane.hole` for named fasteners)

        Args:
            bolt (str): name of the bolt (e.g. `"M3"`)
            depth (float > 0 or None to cut through the entire part): how deep to make the hole
            clearance (float >= 0, optional): additional bolt clearance. Defaults to 0.
        """
        data = boltData(bolt)
        return self.hole(data["diameter"] + clearance, depth)

    def cboreBoltHole(self, bolt: FastenerSpec, depth: Optional[float] = None, clearance = DEFAULT_CLEARANCE, headClearance = DEFAULT_HEAD_DIAMETER_CLEARANCE, cboreDepth: Optional[float] = None):
        """Make a counterbored hole (`cadquery.Workplane.cboreHole` for named fasteners)

        Args:
            bolt (str): name of the bolt (e.g. `"M3"`)
            depth (float > 0 or None to cut through the entire part): how deep to make the hole
            clearance (float >= 0, optional): additional bolt clearance. Defaults to 0.
            headClearance (float >= 0, optional): additional bolt head clearance. Defaults to 0.1.
        """
        data = boltData(bolt, "socket_head")
        cboreD = data["head_diameter"] + clearance + headClearance
        return self.cboreHole(data["diameter"] + clearance, cboreD, cboreDepth = cboreDepth if cboreDepth is not None else data["head_length"], depth = depth)

    def cskBoltHole(self, bolt: FastenerSpec, depth: Optional[float] = None, clearance = DEFAULT_CLEARANCE):
        """Make a countersunk hole (`cadquery.Workplane.cskHole` for named fasteners)

        Args:
            bolt (str): name of the bolt (e.g. `"M3"`)
            depth (float > 0 or None to cut through the entire part): how deep to make the hole
            clearance (float >= 0, optional): additional bolt clearance. Defaults to 0.
        """
        data = boltData(bolt, "countersunk")
        return self.cskHole(data["diameter"] + clearance, data["head_diameter"], cskAngle = 90, depth = depth)
