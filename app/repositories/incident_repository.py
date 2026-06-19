from sqlalchemy.orm import Session 
from app.db.models import Incident 

class IncidentRepository:
    def create(self, db:Session, incident: Incident):
        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident

    def get_all(self, db):
        return db.query(Incident).all()