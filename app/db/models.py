from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime

from app.db.database import Base

class Incident(Base):
    __tablename__ = "incident"

    incident_id = Column(String, primary_key=True)
    alert_name = Column(String)
    service = Column(String)
    severity = Column(String)
    status = Column(String)
    created_at = Column(DateTime)