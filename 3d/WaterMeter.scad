// Itron Aquadis+ DN15 sensor mount for LJ18A3-8Z/BX (M18, Ø18mm)
// Sensor sensing distance: 8mm
// Meter: Itron Aquadis+ R500 16bar T50 (2023)

$fn = 50; // smoother curves for printing

sensor_d = 18;      // LJ18A3 body diameter
sensor_r = sensor_d / 2;  // 9mm
clearance = 0.4;    // printing tolerance

plate_w = 64;
plate_h = 50;
plate_t = 3;

// Sensor holder - tapered cylinder
holder_h = 9;
holder_r1 = 14;     // base radius (Ø28mm footprint)
holder_r2 = sensor_r + clearance + 1.5; // top radius: snug around sensor with wall

// Sensor hole: sized for the actual M18 sensor body + clearance
sensor_hole_r = sensor_r + clearance; // 9.4mm → Ø18.8mm

// Knob clearance
knob_r = 16; // large hole for knob clearance (Ø32mm)

// Corner cuts
corner_cut = 20;

difference() {
  union() {
    // Base plate
    cube([plate_w, plate_h, plate_t]);

    // Sensor holder (tapered cylinder)
    translate([14, 25, 0])
      cylinder(h = holder_h, r1 = holder_r1, r2 = holder_r2);

    // Retention tabs ("ergots") - slightly taller for better grip on meter rim
    translate([-2, 25-2.5, 0]) cube([3, 5, 3]);   // left tab
    translate([60, -2, 0])     cube([4, 3, 3]);    // bottom-right tab
    translate([45, 49, 0])     cube([4, 3, 3]);    // top-right tab
  }
  union() {
    // Sensor through-hole (Ø18.8mm - fits M18 sensor body)
    translate([14, 25, -1])
      cylinder(h = holder_h + plate_t + 2, r = sensor_hole_r);

    // Knob clearance hole
    translate([45, 25, -1])
      cylinder(h = plate_t + 2, r = knob_r);

    // Bottom-left corner (diagonal cut)
    translate([-1, -1, -1])
      linear_extrude(plate_t + 2)
        polygon([[0, 0], [corner_cut + 1, 0], [0, corner_cut + 1]]);

    // Top-left corner (diagonal cut)
    translate([-1, plate_h + 1, -1])
      linear_extrude(plate_t + 2)
        polygon([[0, 0], [corner_cut + 1, 0], [0, -(corner_cut + 1)]]);
  }
}

