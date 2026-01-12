/*
 * Resources for Clipboard Image Control Panel
 * Created by DINKIssTyle on 2026.
 */

#include "Types.r"

/* DITL - Dialog Item List */
resource 'DITL' (-4064, "Main View") {
    {
        /* Item 1: Test Button */
        {10, 10, 30, 120},
        Button {
            enabled,
            "Create Test PICT"
        },
        
        /* Item 2: Status Text */
        {40, 10, 60, 250},
        StaticText {
            disabled,
            "Status: System Ready"
        }
    }
};

/* mach - Machine Compatibility */
resource 'mach' (-4064) {
    0xFFFF, 0xFFFF  /* Run on all machines */
};

/* nrct - Rectangle (Size of the panel) */
resource 'nrct' (-4064) {
    {0, 0, 70, 260} /* Bounds: top, left, bottom, right */
};

/* STR - Version string */
resource 'STR ' (-4064) {
    "Clipboard Image Patch v1.0"
};
