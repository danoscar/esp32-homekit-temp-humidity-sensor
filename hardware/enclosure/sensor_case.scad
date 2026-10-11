// =====================================================================
// ESP32 HomeKit Temp/Humidity Sensor — Enclosure
// =====================================================================
// Two-part screw-together box for the ESP32 devkit and the SHT31/40 breakout.
//
// Measure YOUR actual parts before printing — this is sized generously
// to typical dimensions, not calipered to your exact board. All the
// variables that matter are in the USER-ADJUSTABLE block below.
//
// Render:
//   openscad -D 'PART="base"' -o case_base.stl sensor_case.scad
//   openscad -D 'PART="lid"'  -o case_lid.stl  sensor_case.scad

/* [USER-ADJUSTABLE PARAMETERS] */
PART = "both";

wall        = 2.2;
innerL      = 72;    // fits a 30/38-pin ESP32 devkit lengthwise with margin
innerW      = 34;
baseWallH   = 18;
lidThick    = 3;
lipH        = 4;
cornerR     = 4;

screwInset  = 7;
bossOD      = 7.5;
pilotHoleD  = 2.5;
clearHoleD  = 3.4;
counterboreD= 6.2;
counterboreH= 2.2;

usbCutW     = 10.5;
usbCutH     = 4.2;
usbCutZ     = 8;
usbPortX    = 17;      // USB-C end of the devkit

ventOriginX = 46;      // vent grille over the sensor end of the box
ventOriginY = 6;
ventRows    = 3;
ventCols    = 4;
ventSlotW   = 1.6;
ventSlotL   = 8;
ventSpacing = 3.2;

railH       = 3;
railW       = 2.2;

/* [DERIVED] */
outerL = innerL + 2*wall;
outerW = innerW + 2*wall;
baseOuterH = baseWallH + wall;

module rounded_rect(l, w, r) {
  hull() {
    for (x = [r, l - r])
      for (y = [r, w - r])
        translate([x, y, 0]) circle(r = r, $fn = 48);
  }
}
module rounded_box(l, w, h, r) { linear_extrude(height = h) rounded_rect(l, w, r); }

function boss_positions() = [
  [screwInset, screwInset],
  [outerL - screwInset, screwInset],
  [screwInset, outerW - screwInset],
  [outerL - screwInset, outerW - screwInset]
];

module base() {
  difference() {
    rounded_box(outerL, outerW, baseOuterH, cornerR);
    translate([wall, wall, wall])
      rounded_box(innerL, innerW, baseWallH + 1, max(cornerR - wall, 0.5));
    translate([wall*0.5, wall*0.5, baseOuterH - lipH])
      rounded_box(outerL - wall, outerW - wall, lipH + 1, max(cornerR - wall*0.5, 0.5));
    translate([usbPortX, -0.1, usbCutZ - usbCutH/2])
      cube([usbCutW, wall + 0.2, usbCutH]);
    for (pos = boss_positions())
      translate([pos[0], pos[1], -0.1])
        cylinder(d = pilotHoleD, h = baseOuterH + 0.2, $fn = 24);
  }
  for (pos = boss_positions())
    translate([pos[0], pos[1], wall])
      difference() {
        cylinder(d = bossOD, h = baseWallH - lipH, $fn = 32);
        translate([0, 0, -0.1]) cylinder(d = pilotHoleD, h = baseWallH, $fn = 24);
      }
  // single friction rail pair to hold the devkit edges
  translate([wall + 3, wall + 2, wall]) cube([innerL - 6, railW, railH]);
  translate([wall + 3, wall + innerW - 2 - railW, wall]) cube([innerL - 6, railW, railH]);
}

module lid() {
  difference() {
    union() {
      rounded_box(outerL, outerW, lidThick, cornerR);
      translate([wall*0.5, wall*0.5, -lipH + 0.1])
        rounded_box(outerL - wall - 0.4, outerW - wall - 0.4, lipH, max(cornerR - wall*0.5, 0.5));
    }
    for (pos = boss_positions()) {
      translate([pos[0], pos[1], -0.1])
        cylinder(d = clearHoleD, h = lidThick + lipH + 0.2, $fn = 24);
      translate([pos[0], pos[1], lidThick - counterboreH])
        cylinder(d = counterboreD, h = counterboreH + 0.1, $fn = 32);
    }
    for (r = [0 : ventRows - 1])
      for (c = [0 : ventCols - 1])
        translate([ventOriginX + c*(ventSlotW + ventSpacing),
                   ventOriginY + r*(ventSlotL + ventSpacing),
                   -0.1])
          cube([ventSlotW, ventSlotL, lidThick + 0.2]);
  }
}

if (PART == "base") { base(); }
else if (PART == "lid") { lid(); }
else { base(); translate([outerL + 12, 0, 0]) lid(); }
