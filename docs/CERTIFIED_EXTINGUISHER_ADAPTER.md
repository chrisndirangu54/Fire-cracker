# Certified Extinguisher Adapter

This extension evaluates a commercial extinguisher **for tabletop simulation only**. It does not operate servos, solenoids, valves, release pins, flight controllers or pressure vessels.

Supported candidate classes: water mist, ABC dry chemical, clean agent and CO2. These are **not automatically interchangeable**. Agent selection must be guided by fire class, certified product rating, exposure hazards and qualified fire service assessment.

The `review_extinguisher` function returns an auditable observation, with missing evidence treated as failure. Checks include mounting, pressure, weight-and-balance, thermal limits, manufacturer permission for remote actuation, engineering sign-off, firefighters' authorization, communications and fresh sensing. Even with all checks true, physical release is always disabled.

Potential mechanical concepts for future independent review: manufacturer-approved remote-control extinguisher, tethered fixed-agent supply, or dedicated certified suppression system. Do not modify a commercial extinguisher without its manufacturer's authorization. Bench tests should start with an inert, depressurized mockup. Physical deployment is out of scope.
