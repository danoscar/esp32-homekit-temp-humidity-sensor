#!/usr/bin/env python3
"""
Adds an SHT3x-DIS breakout mount + vent opening to the lid of
"ESP Smart Home Case V2.3" (the flat-floored, tall-walled part of the STL).

usage: python3 add_sht3x_mount.py SOURCE.stl OUT_LID.stl OUT_PLATE.stl [snap|bolt]

SOURCE.stl is the case you download yourself from MakerWorld (see README.md in
this folder). The case files are NOT part of this repository: the MakerWorld
licence does not allow redistributing the original or modified files.

Board assumed (measured from the product photo - verify with calipers):
  12 x 12 mm PCB, 1.6 mm thick, 2 mounting holes ~2 mm dia, 1.5 mm in from each
  side and 1.9 mm up from the bottom edge, chip 3.45 mm up from the bottom edge,
  right-angle 4-pin header on the chip side along the top edge (plastic ~2.5 mm
  tall, pins pointing away from the board).

The board hangs chip-down over a vent opening in the lid floor.
  snap : two locating pegs through the board's holes + two flexible side hooks
         that click over the board's back face. No screws.
  bolt : two standoffs with M2 pilot holes.
Everything is in the lid's own print coordinates (floor outside face z=0,
floor inside face z=1.4, +y wall inner face at y=63.85).
"""
import sys, numpy as np, trimesh
from shapely.geometry import Polygon, box

SRC       = sys.argv[1] if len(sys.argv) > 1 else "source/ESP_Smart_Home_Case_V2.3.stl"
OUT_LID   = sys.argv[2] if len(sys.argv) > 2 else "lid_sht3x_SNAP.stl"
OUT_PLATE = sys.argv[3] if len(sys.argv) > 3 else "plate_sht3x_SNAP.stl"
MODE      = sys.argv[4] if len(sys.argv) > 4 else "snap"

# ---------------- parameters (mm) ----------------
FLOOR_TOP   = 1.4
X_CENTER    = -24.0      # board centre line along x
Y_BOTTOM    = 61.4       # board's screw-hole edge, nearest the +y wall
BOARD_W, BOARD_H, BOARD_T = 12.0, 12.0, 1.6
HOLE_U      = (1.5, 10.5)
HOLE_V      = 1.9
HOLE_D      = 2.0        # board hole diameter (assumed)
CHIP_U, CHIP_V = 5.85, 3.45
STANDOFF_H  = 4.0        # board underside height above the floor
STANDOFF_OD = 4.4
HEADER_H, HEADER_GAP = 2.5, 0.2
RAIL_U, RAIL_V = (0.9, 10.7), (9.4, 11.7)
# bolt mode
PILOT_D, PILOT_DEPTH = 1.8, 3.8
# snap mode
PEG_D       = 1.65       # locating peg (hole 2.0 -> 0.17 clearance per side)
PEG_H       = BOARD_T + 0.5
HOOK_V      = (4.3, 8.7) # hook position along the board (clear of standoffs and rail)
HOOK_SIDE_GAP = 0.15     # gap between board edge and hook arm
HOOK_T      = 0.9        # arm thickness
HOOK_OVERLAP = 0.7       # how far the lip overlaps the board's back face
HOOK_LIP_GAP = 0.15      # clearance between board back face and lip underside
HOOK_RAMP_DEG = 35       # lead-in angle from vertical

def ub(u, v):
    return X_CENTER + (u - BOARD_W / 2), Y_BOTTOM - v

# ---------------- load the lid and close ONLY the logo engraving ----------------
# The lid body is a clean closed shell except for the 0.4 mm logo engraving on its
# outside face, whose letters are open loops at z=0. Those loops are capped with flat
# patches; every other triangle of the original file is left exactly as it was.
import networkx as nx
from functools import reduce
m = trimesh.load(SRC)
parts = m.split(only_watertight=False)
lid = max((p for p in parts if p.bounds[0][1] > 0.5 and p.bounds[1][2] > 20), key=lambda p: len(p.faces))
lid.merge_vertices()
_e = lid.edges_sorted
_u, _inv, _cnt = np.unique(_e, axis=0, return_inverse=True, return_counts=True)
_bad = _u[_cnt == 1]
if len(_bad):
    G = nx.Graph(); G.add_edges_from(map(tuple, _bad))
    loops = [c for comp in nx.connected_components(G) for c in nx.cycle_basis(G.subgraph(comp))]
    polys = [Polygon(lid.vertices[l][:, :2]).buffer(0) for l in loops]
    region = reduce(lambda x, y: x.symmetric_difference(y), polys)
    geoms = [region] if region.geom_type == "Polygon" else list(region.geoms)
    cv, cf, off = [], [], 0
    for g in geoms:
        vv, ff = trimesh.creation.triangulate_polygon(g, engine="earcut")
        cv.append(np.c_[vv, np.zeros(len(vv))]); cf.append(ff + off); off += len(vv)
    cap = trimesh.Trimesh(np.vstack(cv), np.vstack(cf), process=False)
    cap.faces = np.where((cap.face_normals[:, 2] > 0)[:, None], cap.faces[:, ::-1], cap.faces)
    lid = trimesh.util.concatenate([lid, cap]); lid.merge_vertices()
assert lid.is_watertight, "lid is not a closed shell"
_ext = lid.extents
if not np.allclose(_ext, [68.52, 64.8, 21.4], atol=0.5):
    sys.exit("This lid measures %.1f x %.1f x %.1f mm, but the mount coordinates in this script are written "
             "for a 68.5 x 64.8 x 21.4 mm lid (the case as exported with the settings used in this project). "
             "Re-export the case with those settings, or adjust X_CENTER / Y_BOTTOM and the floor values." % tuple(_ext))

def cyl(x, y, r, z0, z1, n=64):
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=n)
    c.apply_translation([x, y, (z0 + z1) / 2]); return c
def prism(poly, z0, z1):
    p = trimesh.creation.extrude_polygon(poly, z1 - z0); p.apply_translation([0, 0, z0]); return p
top = FLOOR_TOP + STANDOFF_H          # board underside z
board_top = top + BOARD_T
adds = []
for u in HOLE_U:
    x, y = ub(u, HOLE_V)
    adds.append(cyl(x, y, STANDOFF_OD / 2, FLOOR_TOP - 0.3, top))
rail_top = top - HEADER_H - HEADER_GAP
(x0, y1), (x1, y0) = ub(RAIL_U[0], RAIL_V[0]), ub(RAIL_U[1], RAIL_V[1])
adds.append(prism(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), FLOOR_TOP - 0.3, rail_top))

if MODE == "snap":
    for u in HOLE_U:                    # locating pegs: straight shank + tapered tip
        x, y = ub(u, HOLE_V)
        adds.append(cyl(x, y, PEG_D / 2, top - 0.1, top + PEG_H - 0.4, 32))
        tip = trimesh.creation.cone(radius=PEG_D / 2, height=0.4, sections=32)
        tip.apply_translation([x, y, top + PEG_H - 0.4]); adds.append(tip)
    # side hooks: profile in (outward distance from the arm's inner face, z), extruded along y
    zlip = board_top + HOOK_LIP_GAP
    ramp_dz = HOOK_OVERLAP / np.tan(np.radians(HOOK_RAMP_DEG))
    prof = Polygon([(0, FLOOR_TOP - 0.5), (0, zlip), (-HOOK_OVERLAP, zlip),
                    (-HOOK_OVERLAP, zlip + 0.3), (0, zlip + 0.3 + ramp_dz),
                    (HOOK_T, zlip + 0.3 + ramp_dz), (HOOK_T, FLOOR_TOP - 0.5)])
    ylo, yhi = Y_BOTTOM - HOOK_V[1], Y_BOTTOM - HOOK_V[0]
    for sgn in (+1, -1):
        h = trimesh.creation.extrude_polygon(prof, yhi - ylo)       # verts: (xl, zl, w)
        V = np.c_[h.vertices[:, 0], h.vertices[:, 2], h.vertices[:, 1]]   # -> (xl, w, zl)
        F = h.faces[:, ::-1]                                          # swapping axes mirrors -> flip winding
        h = trimesh.Trimesh(V, F, process=False)
        h.apply_translation([0, ylo, 0])
        if sgn < 0:
            h.vertices[:, 0] *= -1; h.faces = h.faces[:, ::-1]
        h.apply_translation([X_CENTER + sgn * (BOARD_W / 2 + HOOK_SIDE_GAP), 0, 0])
        adds.append(h)
    print("hook: lip underside z=%.2f, top z=%.2f, arm length %.1f, deflection to clear %.2f mm, est. root strain %.1f%%" % (
        zlip, zlip + 0.3 + ramp_dz, zlip + 0.3 + ramp_dz - FLOOR_TOP,
        HOOK_OVERLAP - HOOK_SIDE_GAP * 0 - 0.0, 150 * HOOK_T * HOOK_OVERLAP / (zlip + 0.3 + ramp_dz - FLOOR_TOP) ** 2))

mount = trimesh.boolean.union(adds, engine="manifold")
if MODE == "bolt":
    for u in HOLE_U:
        x, y = ub(u, HOLE_V)
        mount = trimesh.boolean.difference([mount, cyl(x, y, PILOT_D / 2, top - PILOT_DEPTH, top + 0.5, 32)], engine="manifold")

# ---------------- vent opening ----------------
def stadium(cx, cy, w, l):
    r = w / 2; n = 24
    pts = [(cx + r * np.cos(a), cy + (l / 2 - r) + r * np.sin(a)) for a in np.linspace(0, np.pi, n)] + \
          [(cx + r * np.cos(a), cy - (l / 2 - r) + r * np.sin(a)) for a in np.linspace(np.pi, 2 * np.pi, n)]
    return Polygon(pts)
cutters = []
cx, cy = ub(CHIP_U, 5.0); cutters.append(prism(stadium(cx, cy, 4.0, 7.0), -0.5, FLOOR_TOP + 0.5))
for u in (1.8, 9.9):
    sx, sy = ub(u, 6.8); cutters.append(prism(stadium(sx, sy, 2.0, 4.0), -0.5, FLOOR_TOP + 0.5))

new = trimesh.boolean.union([lid, mount], engine="manifold")
new = trimesh.boolean.difference([new] + cutters, engine="manifold")
assert new.is_watertight
new.export(OUT_LID)

c = m.triangles_center
keep = ~((c[:, 1] > 0.5) & (c[:, 0] < 11.5))
rest = trimesh.Trimesh(m.vertices.copy(), m.faces[keep], process=False); rest.remove_unreferenced_vertices()
trimesh.util.concatenate([rest, new]).export(OUT_PLATE)
print("mode=%s  lid volume %.0f -> %.0f mm3, watertight=%s" % (MODE, lid.volume, new.volume, new.is_watertight))
