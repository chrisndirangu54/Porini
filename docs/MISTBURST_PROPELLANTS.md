# MistBurst propellant and atomizer options

MistBurst compares water (W), approved water-enhancer gel (G), and approved long-term retardant (R) formulations. This is advisory software only.

| Option | Status | Intended research use |
|---|---|---|
| Mechanical pump | Engineering review | Non-gas baseline for compatible liquids |
| Certified compressed air | Engineering review | Gas-assisted atomization subject to certification |
| Certified compressed nitrogen | Engineering review | Inert gas-assisted option; assess asphyxiation risk |
| Chemical gas generator | Simulation only | Hazard and feasibility modelling, not field deployment |

## Safety and compatibility requirements

- Stored-gas systems require certified vessels, regulators, pressure relief devices, inspections, and qualified engineering review.
- Gas generation by chemical reactions carries thermal runaway, overpressure, toxic by-product, and inadvertent activation hazards. No recipes, construction instructions, or ignition controls are included.
- Water, gel, and long-term retardant remain distinct cartridges; do not premix agents without manufacturer approval.
- Nozzle, seals, pump and materials compatibility must be validated for each formulation and propulsion method.
- Environmental protections for people, animals, habitats, and waterways must be verified for any future deployment.
- Dashboard checkboxes are self-declarations, not independently verified certifications.
- Compatibility review never enables physical discharge, drone actuation, or automated cartridge triggering.

## API

- GET /fireshield/mistburst/formulations
- GET /fireshield/mistburst/propellants
- POST /fireshield/mistburst/compatibility-review

The dashboard groups these options under MistBurst FireShield > Atomization and propellant alternatives.