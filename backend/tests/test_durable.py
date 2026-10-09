from datetime import datetime,timezone
from app.durable import DurableStore
from app.models import EventIn
def test_persist_event_and_incident(tmp_path):
    db=str(tmp_path/"porini.sqlite3")
    a=DurableStore(db)
    event=a.ingest(EventIn(source_id="field-mic",modality="acoustic",event_type="unknown_noise",latitude=-1,longitude=37,confidence=.4,severity=2,synthetic=True))
    b=DurableStore(db)
    assert event.id in b.events
    assert event.incident_id in b.incidents
