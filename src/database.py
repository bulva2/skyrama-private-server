from sqlalchemy import create_engine, event, Integer, String, DateTime, Boolean, Index, ForeignKey, BigInteger, UniqueConstraint, func
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from src.enums import PlaneState
from contextlib import contextmanager
import logging

class Base(DeclarativeBase):
    pass

# Plane Table
class Plane(Base):
    __tablename__ = 'planes'

    # Player relationship (n-1)
    owner: Mapped["Player"] = relationship("Player", back_populates="planes")
    
    # Internal global ID for the plane record
    db_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Owner ID -> ID of the player that owns this plane
    owner_id: Mapped[int] = mapped_column(ForeignKey("players.user_id"), nullable=False, index=True)
    
    # Plane ID -> ID of the plane for the player, it is not global ID
    plane_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True) # "id" in JSON
    # Plane type ID -> ID of the plane type (model)
    plane_type_id: Mapped[int] = mapped_column(nullable=False)
    
    # State
    flight_status: Mapped[int] = mapped_column(Integer, default=PlaneState.HANGAR.value)
    container_id: Mapped[int] = mapped_column(Integer, default=-1)
    subcontainer_id: Mapped[int] = mapped_column(Integer, default=-1)
    
    # Timestamps (BigInt for unix timestamps)
    departure_time: Mapped[int] = mapped_column(BigInteger, default=0)
    arrival_time: Mapped[int] = mapped_column(BigInteger, default=0)
    start_service_time: Mapped[int] = mapped_column(BigInteger, default=0)
    last_state_change_time: Mapped[int] = mapped_column(BigInteger, default=0)
    
    # Flight details
    from_player_id: Mapped[int] = mapped_column(Integer, default=0) # "player_id" in JSON usually denotes owner, but "from_user_name" exists
    from_user_object_id: Mapped[int] = mapped_column(Integer, default=-1)  # Original plane ID on sender's airport
    to_player_id: Mapped[int] = mapped_column(Integer, default=-1)
    from_location_id: Mapped[int] = mapped_column(Integer, default=-1)
    to_location_id: Mapped[int] = mapped_column(Integer, default=-1)
    from_user_name: Mapped[str] = mapped_column(String(20), default="")
    to_user_name: Mapped[str] = mapped_column(String(20), default="")
    
    # Stats / Configuration
    active_count: Mapped[int] = mapped_column(Integer, default=1)
    contents_count: Mapped[int] = mapped_column(Integer, default=0)
    wares_revenue: Mapped[int] = mapped_column(Integer, default=0)
    buddy_points: Mapped[int] = mapped_column(Integer, default=0)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    air_coins: Mapped[int] = mapped_column(Integer, default=0)
    kerosene_boost_flag: Mapped[int] = mapped_column(Integer, default=0)
    instantland: Mapped[int] = mapped_column(Integer, default=0)
    upgrade_level: Mapped[int] = mapped_column(Integer, default=0)
    
    # Drops / Items
    souvenir_types_id: Mapped[int] = mapped_column(Integer, default=-1)
    drop_consumable_id: Mapped[int] = mapped_column(Integer, default=0)
    drop_consumable_amount: Mapped[int] = mapped_column(Integer, default=0)
    drop_material: Mapped[int] = mapped_column(Integer, default=0)
    drop_material_amount: Mapped[int] = mapped_column(Integer, default=0)
    banner_id: Mapped[int] = mapped_column(Integer, default=-1)
    banner_text: Mapped[str] = mapped_column(String(500), default="")  # Custom text for fly-by banners

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

    # Plane relationship (1-n)
    planes: Mapped[list["Plane"]] = relationship("Plane", back_populates="owner", cascade="all, delete-orphan")
    chat_messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    
    # Primary identifications
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    token: Mapped[str] = mapped_column(String(36), index=True)
    location_id: Mapped[int] = mapped_column(Integer, default=-1, index=True)

    # Player states
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_user_being_log_traced: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Session data
    last_login: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    saved_sequence_num: Mapped[int] = mapped_column(Integer, default=-1) # unused
    
    # Data blobs
    player_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    account_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    goals_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Player item collections
    backgrounds: Mapped[list] = mapped_column(JSONB, default=list)
    landmarks: Mapped[list] = mapped_column(JSONB, default=list)
    consumables: Mapped[list] = mapped_column(JSONB, default=list)
    runways: Mapped[list] = mapped_column(JSONB, default=list)
    terminals: Mapped[list] = mapped_column(JSONB, default=list)
    hangars: Mapped[list] = mapped_column(JSONB, default=list)
    landside_buildings: Mapped[list] = mapped_column(JSONB, default=list)
    cargo_shops: Mapped[list] = mapped_column(JSONB, default=list)
    cargo: Mapped[list] = mapped_column(JSONB, default=list)
    warehouses: Mapped[list] = mapped_column(JSONB, default=list)
    bays: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Buddies and buddy points
    buddy_stuff: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Other game data
    souvenir_collections: Mapped[list] = mapped_column(JSONB, default=list)
    lucky_luggage_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    crafting_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    expedition_status: Mapped[dict] = mapped_column(JSONB, default=dict) # never released feature
    
    # Location/world map data (per-player visited status)
    locations: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Special/event buildings
    special_buildings: Mapped[list] = mapped_column(JSONB, default=list)
    
    # News/messages
    news: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Event and crafting materials
    event_materials: Mapped[list] = mapped_column(JSONB, default=list)
    materials: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Recycling and crafting slots
    user_recycling_slots: Mapped[list] = mapped_column(JSONB, default=list)
    user_crafting_slots: Mapped[list] = mapped_column(JSONB, default=list)
    user_current_craftings: Mapped[list] = mapped_column(JSONB, default=list)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_token', 'token'),
        Index('idx_location_id', 'location_id'),
        Index('idx_username_lower', func.lower(username)),
    )

def update_timestamp(mapper, connection, target):
    target.updated_at = datetime.now()

event.listen(Player, 'before_update', update_timestamp)

class Voucher(Base):
    __tablename__ = 'vouchers'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Voucher identification
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Rewards (in JSON)
    # Contains: air_coins, air_cash, passengers, xp, super_fuel, etc.
    rewards: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Usage limits
    max_uses: Mapped[int] = mapped_column(Integer, nullable=True)  # NULL = unlimited
    current_uses: Mapped[int] = mapped_column(Integer, default=0)
    
    # Expiration
    expires: Mapped[int] = mapped_column(Integer, nullable=True)  # Unix timestamp, NULL = never expires
    
    # Status
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_active', 'active'),
    )

class VoucherRedemption(Base):
    """Track which users have redeemed which vouchers"""
    __tablename__ = 'voucher_redemptions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    voucher_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    redeemed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_voucher', 'user_id', 'voucher_id', unique=True),  # Prevent duplicate redemptions
    )

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    user: Mapped["Player"] = relationship("Player", back_populates="chat_messages")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.user_id"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    
    __table_args__ = (
        Index('idx_created_at', 'created_at'),
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