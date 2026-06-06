from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class DBLead(Base):
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_name = Column(String, index=True)
    decision_maker_name = Column(String)
    phone_number = Column(String)
    email_address = Column(String)
    social_media_link = Column(String)
    lead_status = Column(String)
    confidence_score = Column(Integer)
    reasoning_log = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "business_name": self.business_name,
            "decision_maker_name": self.decision_maker_name,
            "phone_number": self.phone_number,
            "email_address": self.email_address,
            "social_media_link": self.social_media_link,
            "lead_status": self.lead_status,
            "confidence_score": self.confidence_score,
            "reasoning_log": self.reasoning_log,
            "created_at": str(self.created_at)
        }


def setup_database(db_path: str = "sqlite:///data/leads.db"):
    engine = create_engine(db_path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal
