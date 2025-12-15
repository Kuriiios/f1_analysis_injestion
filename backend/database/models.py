from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, SmallInteger, Text, Interval, Float
from sqlalchemy.orm import relationship
from .db_init import Base

class Compound(Base):
    __tablename__ = 'compound'

    id = Column(Integer, primary_key=True)
    hardness = Column(String(2), nullable=False, unique=True)

    event_round_soft = relationship('EventRound', back_populates='soft_compound', foreign_keys='EventRound.soft_compound_id')

    event_round_medium = relationship('EventRound', back_populates='medium_compound', foreign_keys='EventRound.medium_compound_id')

    event_round_hard = relationship('EventRound', back_populates='hard_compound', foreign_keys='EventRound.hard_compound_id')

class Tyre(Base):
    __tablename__ = 'tyre'

    id = Column(Integer, primary_key=True)
    name = Column(String(15), nullable=False, unique=True)

    lap = relationship('Lap', back_populates='tyre')

class WindDirection(Base):
    __tablename__ = 'wind_direction'

    id = Column(Integer, primary_key=True)
    cardinal_direction = Column(String(3), nullable=False, unique=True)

class EventRound(Base):
    __tablename__ = 'event_round'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    round_number = Column(SmallInteger, nullable=False)
    year = Column(SmallInteger, nullable=False)
    date = Column(Date, nullable=True, unique=True)
    country = Column(String(30))
    location = Column(String(30))
    is_sprint_event = Column(Boolean, nullable=False)

    soft_compound_id = Column(Integer, ForeignKey('compound.id'))
    soft_compound = relationship('Compound', back_populates='event_round_soft', foreign_keys=[soft_compound_id])

    medium_compound_id = Column(Integer, ForeignKey('compound.id'))
    medium_compound = relationship('Compound', back_populates='event_round_medium', foreign_keys=[medium_compound_id])

    hard_compound_id = Column(Integer, ForeignKey('compound.id'))
    hard_compound = relationship('Compound', back_populates='event_round_hard',foreign_keys=[hard_compound_id])

    event_session = relationship('EventSession', back_populates='event_round')

class SessionName(Base):
    __tablename__ = 'session_name'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=True, unique=True)

    event_session = relationship('EventSession', back_populates='session_name')

class Driver(Base):
    __tablename__ = 'driver'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True, unique=True)
    number = Column(Integer, nullable=False)
    abbreviation = Column(String(3))
    country = Column(String(30))
    hex_code = Column(String(7))

    dta = relationship('Dta', back_populates='driver')

class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True, unique=True)
    abbreviation = Column(String(3), nullable=False)
    country = Column(String(30))
    hex_code = Column(String(7))

    dta = relationship('Dta', back_populates='team')

class EventSession(Base):
    __tablename__ = 'event_session'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    
    event_round_id = Column(Integer, ForeignKey('event_round.id'))
    event_round = relationship('EventRound', back_populates='event_session')
    
    session_name_id = Column(Integer, ForeignKey('session_name.id'))
    session_name = relationship('SessionName', back_populates='event_session')
    
    weather = relationship('Weather', back_populates='event_session')
    
    race_control = relationship('RaceControl', back_populates='event_session')
    
    team_radio = relationship('TeamRadio', back_populates='event_session')

    dta = relationship('Dta', back_populates='event_session')

class Weather(Base):
    __tablename__ = 'weather'

    id = Column(Integer, primary_key=True)
    time = Column(Interval, nullable=False)
    air_temp = Column(SmallInteger)
    humidity = Column(SmallInteger)
    pressure = Column(SmallInteger)
    track_temp = Column(SmallInteger)
    wind_speed = Column(SmallInteger)
    wind_direction = Column(SmallInteger)
    is_rainfall = Column(Boolean)

    event_session_id = Column(Integer, ForeignKey('event_session.id'))
    event_session = relationship('EventSession', back_populates='weather')

class RaceControl(Base):
    __tablename__ = 'race_control'

    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=True, unique=True)
    date = Column(Date, nullable=True, unique=True)

    event_session_id = Column(Integer, ForeignKey('event_session.id'))
    event_session = relationship('EventSession', back_populates='race_control')

class TeamRadio(Base):
    __tablename__ = 'team_radio'

    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=True, unique=True)
    url = Column(String(255), nullable=True, unique= True)
    date = Column(Date, nullable=True, unique=True)

    event_session_id = Column(Integer, ForeignKey('event_session.id'))
    event_session = relationship('EventSession', back_populates='team_radio')

class Dta(Base):
    __tablename__ = 'dta'

    id = Column(Integer, primary_key=True)

    driver_id = Column(Integer, ForeignKey('driver.id'))
    driver = relationship('Driver', back_populates='dta')

    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship('Team', back_populates='dta')

    event_session_id = Column(Integer, ForeignKey('event_session.id'))
    event_session = relationship('EventSession', back_populates='dta')

    lap = relationship('Lap', back_populates='dta')
    
    pos_data = relationship('PosData', back_populates='dta')
    
    car_data = relationship('CarData', back_populates='dta')

class Drs(Base):
    __tablename__ = 'drs'

    id = Column(Integer, primary_key=True)
    status = Column(String(15), nullable=False, unique=True)

class Lap(Base):
    __tablename__ = 'lap'

    id = Column(Integer, primary_key=True)
    laptime_ms = Column(Integer, nullable=False)
    lap_number = Column(SmallInteger)
    sector_1 = Column(Integer)
    sector_2 = Column(Integer)
    sector_3 = Column(Integer)
    stint = Column(SmallInteger)
    speed_i1 = Column(SmallInteger)
    speed_i2 = Column(SmallInteger)
    speed_fl = Column(SmallInteger)
    speed_st = Column(SmallInteger)
    tyre_life = Column(SmallInteger)
    position = Column(SmallInteger)
    sector_1_time = Column(Interval)
    sector_2_time = Column(Interval)
    sector_3_time = Column(Interval)
    pit_in_time = Column(Interval)
    pit_out_time = Column(Interval)
    start_time = Column(Interval, nullable=False)
    start_date = Column(Date, nullable=False)
    is_personal_best = Column(Boolean)
    is_deleted = Column(Boolean)
    is_accurate = Column(Boolean)
    track_status = Column(Integer)

    dta_id = Column(Integer, ForeignKey('dta.id'))
    dta = relationship('Dta', back_populates='lap')
    
    tyre_id = Column(Integer, ForeignKey('tyre.id'))
    tyre = relationship('Tyre', back_populates='lap')

class CarData(Base):
    __tablename__ = 'car_data'

    id = Column(Integer, primary_key=True)
    rpm = Column(SmallInteger)
    speed = Column(SmallInteger)
    gear = Column(SmallInteger)
    throttle = Column(SmallInteger)
    is_braking = Column(Boolean)
    time_ms = Column(Integer, nullable=False)
    session_time = Column(Interval, nullable=False)
    date = Column(Date, nullable=False)
    distance = Column(Float)
    differential_distance = Column(Float)
    relative_distance = Column(Float)
    distance_driver_ahead = Column(Float)
    track_status = Column(Integer)

    dta_id = Column(Integer, ForeignKey('dta.id'))
    dta = relationship('Dta', back_populates='car_data')

class PosData(Base):
    __tablename__ = 'pos_data'

    id = Column(Integer, primary_key=True)
    x = Column(SmallInteger)
    y = Column(SmallInteger)
    z = Column(SmallInteger)
    time_ms = Column(Integer, nullable=False)
    session_time = Column(Interval, nullable=False)
    date = Column(Date, nullable=False)
    is_on_track = Column(Boolean)
    track_status = Column(Integer)

    dta_id = Column(Integer, ForeignKey('dta.id'))
    dta = relationship('Dta', back_populates='pos_data')