# FireShield hybrid suppression advisor
This is a **non-operational planning aid** for Porini wildfire incident teams, to complement existing `backend/app/fireshield.py`. The new `backend/app/hybrid_suppression.py` module compares candidate *liquid* agents (water cooling, professionally approved long-term vegetation retardants, and approved Class A wetting agents) while excluding dropped gas munitions and reactive capsules. It does not prescribe chemical concentrations, nozzle specifications or flight patterns.

## Safety gates
All scenario flags fail closed; human and wildlife clearance, fresh sensor evidence, incident-command authorization and environmental review are prerequisites even to mark a *simulation* ready. Wind drift and waterway restrictions produce blocking warnings. The module returns **no** actuator commands or release controls. Run it only for a tabletop exercise; actual use requires qualified fire services and regulatory/ecological approvals.

## Indoor fire-rescue counterpart
A separate indoor Python prototype uses `suppression_planner.py`, with candidate water-mist and certified stationary clean-agent concepts. No live chemical reaction, compressed-gas munition or physical release is implemented.
