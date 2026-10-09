# Flutter Ranger App — implementation specification

The current interactive ranger workflow lives in the React dashboard and FastAPI endpoints. A native Flutter app is **not built yet**.

Required functionality: Firebase Auth or OIDC, tenant-specific access, offline encrypted SQLite queue, incident acknowledgements, geospatial offline tiles, audio/images evidence provenance, secure push-to-talk, SOS, veterinary referrals, bilingual localization, accessibility, battery-aware GPS sharing, precise controls over exposure of sensitive animal locations.

Suggested packages after evaluation: flutter_map, drift, dio, connectivity_plus, firebase_messaging, flutter_secure_storage. Provide emulator tests and manual field drills before launch.
