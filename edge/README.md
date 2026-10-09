# Porini Edge Ingestion

For an edge acoustic or camera gateway, produce validated JSON matching `EventIn` and send via `POST /events` using a per-device credential when deployed. A basic MQTT payload-to-event adapter is available at `backend/app/connectors.py` but **no broker listener is running**.

Recommended open source projects to evaluate: BirdNET-Analyzer for bird activity; OpenSoundscape and librosa for soundscape research; PANNs/YAMNet-style models for general event candidates; Ultralytics YOLO (check license requirements), MegaDetector and PyTorch for camera-trap analysis; OpenCV for visible imagery; ONNX Runtime for edge deployment.

Do not treat generic sound classifiers as validated gunshot detectors. Ground truth, location estimation and cross-sensor confirmation are required.

Gateway security backlog: mutual TLS MQTT, device registration, key rotation, replay-resistant nonces, encrypted offline queue, clock synchronization and rate limiting.
