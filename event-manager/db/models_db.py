from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from .database import Base


join_pe = Table('JOIN_PE', Base.metadata,
                Column('PachetID', Integer, ForeignKey('PACHETE.ID'), primary_key=True),
                Column('EvenimentID', Integer, ForeignKey('EVENIMENTE.ID'), primary_key=True)
                )

class Utilizator(Base):
    __tablename__ = "UTILIZATORI"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    parola = Column(String(255), nullable=False)
    rol = Column(Enum('admin', 'owner-event', 'client'), nullable=False)


class Eveniment(Base):
    __tablename__ = "EVENIMENTE"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_OWNER = Column(Integer, ForeignKey("UTILIZATORI.ID"), nullable=False)
    nume = Column(String(100), unique=True, nullable=False)
    locatie = Column(String(100))
    descriere = Column(Text)
    numarLocuri = Column(Integer)

    # Relatii
    pachete = relationship("Pachet", secondary=join_pe, back_populates="evenimente")
    bilete = relationship("Bilet", back_populates="eveniment")


class Pachet(Base):
    __tablename__ = "PACHETE"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_OWNER = Column(Integer, ForeignKey("UTILIZATORI.ID"), nullable=False)
    nume = Column(String(100), unique=True, nullable=False)
    locatie = Column(String(100))
    descriere = Column(Text)
    numarLocuri = Column(Integer)

    # Relatii
    evenimente = relationship("Eveniment", secondary=join_pe, back_populates="pachete")
    bilete = relationship("Bilet", back_populates="pachet")


class Bilet(Base):
    __tablename__ = "BILETE"

    COD = Column(String(100), primary_key=True)
    PachetID = Column(Integer, ForeignKey("PACHETE.ID"), nullable=True)
    EvenimentID = Column(Integer, ForeignKey("EVENIMENTE.ID"), nullable=True)

    # Relatii
    pachet = relationship("Pachet", back_populates="bilete")
    eveniment = relationship("Eveniment", back_populates="bilete")