from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Index, ForeignKey, BigInteger, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from contextlib import contextmanager
import logging

# To-do?: Possibly change Columns to mapped_column in the future
Base = declarative_base()

# Plane Table
class Plane(Base):
    __tablename__ = 'planes'
    
    # Internal DB ID
    db_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey('players.user_id'), nullable=False, index=True)
    
    # Plane Data
    plane_id = Column(Integer, nullable=False, index=True) # "id" in JSON
    plane_type_id = Column(Integer, nullable=False)
    
    # State
    flight_status = Column(Integer, default=77)
    container_id = Column(Integer, default=-1)
    subcontainer_id = Column(Integer, default=-1)
    
    # Timestamps (BigInt for unix timestamps)
    departure_time = Column(BigInteger, default=0)
    arrival_time = Column(BigInteger, default=0)
    start_service_time = Column(BigInteger, default=0)
    last_state_change_time = Column(BigInteger, default=0)
    
    # Flight details
    from_player_id = Column(Integer, default=0) # "player_id" in JSON usually denotes owner, but "from_user_name" exists
    from_user_object_id = Column(Integer, default=-1)  # Original plane ID on sender's airport
    to_player_id = Column(Integer, default=-1)
    from_location_id = Column(Integer, default=-1)
    to_location_id = Column(Integer, default=-1)
    from_user_name = Column(String(50), default="")
    to_user_name = Column(String(50), default="")
    
    # Stats / Configuration
    active_count = Column(Integer, default=1)
    contents_count = Column(Integer, default=0)
    wares_revenue = Column(Integer, default=0)
    buddy_points = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    air_coins = Column(Integer, default=0)
    kerosene_boost_flag = Column(Integer, default=0)
    instantland = Column(Integer, default=0)
    upgrade_level = Column(Integer, default=0)
    
    # Drops / Items
    souvenir_types_id = Column(Integer, default=-1)
    drop_consumable_id = Column(Integer, default=0)
    drop_consumable_amount = Column(Integer, default=0)
    drop_material = Column(Integer, default=0)
    drop_material_amount = Column(Integer, default=0)
    banner_id = Column(Integer, default=-1)
    banner_text = Column(String(500), default="")  # Custom text for fly-by banners

    # Relationships
    owner = relationship("Player", back_populates="planes_rel")

    __table_args__ = (
        UniqueConstraint('owner_id', 'plane_id', name='uix_owner_plane'),
    )
    
    def to_dict(self):
        return {
            "souvenir_types_id": self.souvenir_types_id,
            "active_count": self.active_count,
            "id": self.plane_id,
            "plane_type_id": self.plane_type_id,
            "container_id": self.container_id,
            "subcontainer_id": self.subcontainer_id,
            "to_player_id": self.to_player_id,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "kerosene_boost_flag": self.kerosene_boost_flag,
            "flight_status": self.flight_status,
            "buddy_points": self.buddy_points,
            "contents_count": self.contents_count,
            "air_coins": self.air_coins,
            "xp": self.xp,
            "wares_revenue": self.wares_revenue,
            "banner_id": self.banner_id,
            "banner_text": self.banner_text,
            "start_service_time": self.start_service_time,
            "last_state_change_time": self.last_state_change_time,
            "drop_consumable_id": self.drop_consumable_id,
            "drop_consumable_amount": self.drop_consumable_amount,
            "instantland": self.instantland,
            "player_id": self.from_player_id,
            "fromUser_objectId": self.from_user_object_id,
            "from_location_id": self.from_location_id,
            "from_user_name": self.from_user_name,
            "upgrade_level": self.upgrade_level,
            "to_location_id": self.to_location_id,
            "to_user_name": self.to_user_name,
            "drop_material": self.drop_material,
            "drop_material_amount": self.drop_material_amount
        }

# Main Player Table
class Player(Base):
    __tablename__ = 'players'
    
    # Primary identification
    user_id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    token = Column(String(36), index=True)
    location_id = Column(Integer, default=-1, index=True)
    
    # Session data
    last_login = Column(DateTime, default=datetime.utcnow)
    
    # Game state tracking
    saved_sequence_num = Column(Integer, default=-1)
    is_user_being_log_traced = Column(Boolean, default=False)
    
    player_data = Column(JSONB, nullable=False)
    account_data = Column(JSONB, nullable=False)
    goals_data = Column(JSONB, nullable=False)
    
    # Collections (as JSONB arrays)
    backgrounds = Column(JSONB, default=list)
    landmarks = Column(JSONB, default=list)
    consumables = Column(JSONB, default=list)
    runways = Column(JSONB, default=list)
    terminals = Column(JSONB, default=list)
    hangars = Column(JSONB, default=list)
    
    planes_rel = relationship("Plane", back_populates="owner", cascade="all, delete-orphan")
    landside_buildings = Column(JSONB, default=list)
    cargo_shops = Column(JSONB, default=list)
    cargo = Column(JSONB, default=list)
    warehouses = Column(JSONB, default=list)
    bays = Column(JSONB, default=list)
    
    # Buddy system
    buddy_stuff = Column(JSONB, default=dict)  # buddyStuff object
    
    # Other game data
    souvenir_collections = Column(JSONB, default=list)
    lucky_luggage_data = Column(JSONB, default=dict)
    crafting_data = Column(JSONB, default=dict)
    expedition_status = Column(JSONB, default=dict)
    
    # Location/world map data (per-player visited status)
    locations = Column(JSONB, default=list)
    
    # Special/event buildings
    special_buildings = Column(JSONB, default=list)
    
    # News/messages
    news = Column(JSONB, nullable=True)
    
    # Event and crafting materials
    event_materials = Column(JSONB, default=list)
    materials = Column(JSONB, default=dict)
    
    # Recycling and crafting slots
    user_recycling_slots = Column(JSONB, default=list)
    user_crafting_slots = Column(JSONB, default=list)
    user_current_craftings = Column(JSONB, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_token', 'token'),
        Index('idx_location_id', 'location_id'),
        Index('idx_username_lower', func.lower(username)),
    )

class Voucher(Base):
    __tablename__ = 'vouchers'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Voucher identification
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    
    # Rewards (stored as JSONB for flexibility)
    # Contains: air_coins, air_cash, passengers, xp, super_fuel, etc.
    rewards = Column(JSONB, nullable=False)
    
    # Usage limits
    max_uses = Column(Integer, nullable=True)  # NULL = unlimited
    current_uses = Column(Integer, default=0)
    
    # Expiration
    expires = Column(Integer, nullable=True)  # Unix timestamp, NULL = never expires
    
    # Status
    active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_active', 'active'),
    )

class VoucherRedemption(Base):
    """Track which users have redeemed which vouchers"""
    __tablename__ = 'voucher_redemptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    voucher_id = Column(Integer, nullable=False, index=True)
    redeemed_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_voucher', 'user_id', 'voucher_id', unique=True),  # Prevent duplicate redemptions
    )

class DatabaseManager:
    def __init__(self, connection_string):
        self.engine = create_engine(
            connection_string,
            pool_size=50,
            max_overflow=50,
            pool_pre_ping=True,
            echo=False
        )
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        logging.info("Database connection established!")
    
    def create_tables(self): 
        Base.metadata.create_all(self.engine)
        logging.info("Database tables created.")

    def get_session(self):
        return self.Session()
    
    def close_session(self):
        self.Session.remove()

db_manager: DatabaseManager | None = None

def init_database(connection_string):
    global db_manager
    db_manager = DatabaseManager(connection_string)
    return db_manager

def get_db_session():
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database(connection_string) first.")
    return db_manager.get_session()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if db_manager:
            db_manager.close_session()