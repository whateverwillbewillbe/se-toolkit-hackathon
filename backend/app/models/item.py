from sqlalchemy import Column, Integer, String, BigInteger, Boolean
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, default="Другое")
    is_bought = Column(Boolean, default=False, nullable=False)
    user_id = Column(BigInteger, nullable=False, index=True)

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', category='{self.category}', is_bought={self.is_bought}, user_id={self.user_id})>"
