from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from contextlib import contextmanager
import logging

# To-do?: Possibly change Columns to mapped_column in the future
Base = declarative_base()

# Main Player Table
class Player(Base):
    __tablename__ = 'players'
    
    # Primary identification
    user_id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    token = Column(String(36), index=True)
    
    # Player stats (frequently accessed)
    air_coins = Column(Integer, default=0)
    air_cash = Column(Integer, default=0)
    event_currency = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    super_fuel = Column(Integer, default=0)
    passengers = Column(Integer, default=0)
    location_id = Column(Integer, default=-1, index=True)  # I suppose we should index this for the map
    
    # Session data
    last_buddyping_time = Column(Integer, default=0)
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
    planes = Column(JSONB, default=list)
    consumables = Column(JSONB, default=list)
    runways = Column(JSONB, default=list)
    terminals = Column(JSONB, default=list)
    hangars = Column(JSONB, default=list)
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
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            echo=True
        )
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        logging.info("[DB] Connection established.")
    
    def create_tables(self): 
        Base.metadata.create_all(self.engine)
        logging.info("[DB] Tables created.")

    def get_session(self):
        return self.Session()
    
    def close_session(self):
        self.Session.remove()

db_manager = None

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
        db_manager.close_session()