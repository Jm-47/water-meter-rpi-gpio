// Itron Aquadis+ DN15 sensor mount for LJ18A3-8Z/BX (M18, Ø18mm)
// Sensor sensing distance: 8mm
// Meter: Itron Aquadis+ R500 16bar T50 (2023)

$fn = 50; // smoother curves for printing

plate_w = 68;
plate_h = 54;
plate_t = 2;

l = 5;

// Sensor holder - tapered cylinder
holder_h = 9;
holder_r1 = 13.5; // base radius
holder_r2 = 10.5; // top radius

// Sensor hole: sized for the actual M18 sensor body
sensor_hole_r = 8.9;

difference() {
  union() {
    difference() {
      union() {
        // Base plate
        translate([plate_h/2, 0, 0])       cube([plate_w-plate_h/2, plate_h, plate_t]);
        translate([plate_h/2, plate_h/2]) cylinder(h = plate_t, r = plate_h/2);

        // Retention tabs ("ergots") - slightly taller for better grip on meter rim
        translate([-2, 20.5, 0])        cube([3, 5, 2]);   // bottom tab
        translate([plate_w - 4, -2, 0]) cube([4, 7, 4]);   // top-right tab
        translate([45, 49, 0])          cube([4, 7, 4]);   // left tab
      }
      union() {
        translate([plate_h/2, l, -1])         cube([plate_w - l - plate_h/2, plate_h - 2*l, plate_t + 2]);  
        translate([plate_h/2, plate_h/2, -1]) cylinder(h = plate_t+2, r = (plate_h)/2-l);
      }
    }

    // Sensor holder
    translate([14, 23, 0])  cylinder(h = holder_h, r1 = holder_r1, r2 = holder_r2);
  }

  // Sensor through-hole
  translate([14, 23, -1]) cylinder(h = holder_h + 2, r = sensor_hole_r);
}