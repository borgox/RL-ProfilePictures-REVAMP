import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, Date,
    Text, Float, Index, UniqueConstraint, func, text
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class AvatarRequest(Base):
    __tablename__ = "avatar_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    request_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cache_hit = Column(Boolean, default=False)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    ip_address = Column(String(45), index=True)
    user_agent = Column(Text)
    response_time_ms = Column(Integer)
    referer = Column(Text)
    
    __table_args__ = (
        Index('idx_avatar_requests_platform_user', 'platform', 'user_id'),
        Index('idx_avatar_requests_timestamp', 'request_timestamp'),
        Index('idx_avatar_requests_ip', 'ip_address'),
    )


class RateLimitTracking(Base):
    __tablename__ = "rate_limit_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    request_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    endpoint = Column(String(255), nullable=False)
    user_agent = Column(Text)
    
    __table_args__ = (
        Index('idx_rate_limit_ip_timestamp', 'ip_address', 'request_timestamp'),
    )


class CacheMetadata(Base):
    __tablename__ = "cache_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    created_timestamp = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=1)
    
    __table_args__ = (
        UniqueConstraint('platform', 'user_id', name='uq_cache_metadata_platform_user'),
        Index('idx_cache_metadata_platform_user', 'platform', 'user_id'),
    )


class UserAnalytics(Base):
    __tablename__ = "user_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, unique=True, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    total_requests = Column(Integer, default=1)
    unique_platforms = Column(Integer, default=1)
    platforms_used = Column(Text)
    user_agent = Column(Text)
    country = Column(String(100))
    city = Column(String(100))
    is_bot = Column(Boolean, default=False)


class DailyStats(Base):
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)  # <-- FIX
    total_requests = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    cache_hits = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    steam_requests = Column(Integer, default=0)
    xbox_requests = Column(Integer, default=0)
    psn_requests = Column(Integer, default=0)
    switch_requests = Column(Integer, default=0)
    epic_requests = Column(Integer, default=0)
    total_bandwidth_mb = Column(Float, default=0.0)
    avg_response_time_ms = Column(Float, default=0.0)


class HourlyStats(Base):
    __tablename__ = "hourly_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(String(19), nullable=False, unique=True, index=True)
    requests = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    cache_hits = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    bandwidth_mb = Column(Float, default=0.0)


class ErrorLogs(Base):
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    platform = Column(String(50))
    user_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    stack_trace = Column(Text)


class UserHeartbeats(Base):
    __tablename__ = "user_heartbeats"
    
    platform = Column(String(20), primary_key=True, nullable=False)
    user_id = Column(String(255), primary_key=True, nullable=False)
    last_heartbeat = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(String(10), default="online", nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_heartbeat_time', 'last_heartbeat'),
        Index('idx_heartbeat_status', 'status'),
        Index('idx_heartbeat_platform_user', 'platform', 'user_id'),
    )


class Database:
    def __init__(self):
        self.engine = None
        self.async_session = None
        
    async def initialize(self):
        """Initialize database connection and create tables."""
        try:
            # Create async engine
            self.engine = create_async_engine(
                settings.database_url,
                echo=settings.debug,
                pool_size=40, # TEMP was 20
                max_overflow=80, # TEMP, was 40
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Create async session factory
            self.async_session = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create all tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("PostgreSQL database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL database: {e}")
            raise
    
    def get_session(self) -> AsyncSession:
        """Get database session."""
        if not self.async_session:
            raise RuntimeError("Database not initialized")
        return self.async_session()
    
    async def log_avatar_request(self, platform: str, user_id: str, cache_hit: bool, 
                                success: bool, error_message: Optional[str] = None, 
                                ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                                response_time_ms: Optional[int] = None, referer: Optional[str] = None):
        """Log an avatar request with comprehensive tracking."""
        async with self.get_session() as session:
            try:
                avatar_request = AvatarRequest(
                    platform=platform,
                    user_id=user_id,
                    cache_hit=cache_hit,
                    success=success,
                    error_message=error_message,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    response_time_ms=response_time_ms,
                    referer=referer
                )
                session.add(avatar_request)
                #await session.commit()
                
                # Update user analytics
                if ip_address:
                    await self._update_user_analytics(session, ip_address, platform, user_agent)
                
                # Update daily stats
                await self._update_daily_stats(session, platform, success, cache_hit, response_time_ms)
                
                # Update hourly stats
                await self._update_hourly_stats(session, success, cache_hit, response_time_ms)
                
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error logging avatar request: {e}")
                raise
    
    async def log_rate_limit_request(self, ip_address: str, endpoint: str, user_agent: Optional[str] = None):
        """Log a rate limit request."""
        async with self.get_session() as session:
            try:
                rate_limit = RateLimitTracking(
                    ip_address=ip_address,
                    endpoint=endpoint,
                    user_agent=user_agent
                )
                session.add(rate_limit)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error logging rate limit request: {e}")
                raise
    
    async def get_recent_requests(self, ip_address: str, minutes: int = 1) -> int:
        """Get number of recent requests from an IP address."""
        async with self.get_session() as session:
            try:
                from sqlalchemy import select, func
                result = await session.execute(
                    select(func.count(RateLimitTracking.id))
                    .where(
                        RateLimitTracking.ip_address == ip_address,
                        RateLimitTracking.request_timestamp > func.now() - text(f"interval '{minutes} minutes'")
                    )
                )
                return result.scalar() or 0
            except Exception as e:
                logger.error(f"Error getting recent requests: {e}")
                return 0
    
    async def update_cache_metadata(self, platform: str, user_id: str, file_path: str, file_size: int):
        """Update cache metadata using UPSERT to handle concurrent requests."""
        async with self.get_session() as session:
            try:
                from sqlalchemy.dialects.postgresql import insert
                from sqlalchemy import select
                
                # Use PostgreSQL's ON CONFLICT to handle concurrent inserts
                stmt = insert(CacheMetadata).values(
                    platform=platform,
                    user_id=user_id,
                    file_path=file_path,
                    file_size_bytes=file_size,
                    created_timestamp=datetime.utcnow(),
                    last_accessed=datetime.utcnow(),
                    access_count=1
                )
                
                # On conflict, update the existing record
                stmt = stmt.on_conflict_do_update(
                    index_elements=['platform', 'user_id'],
                    set_={
                        'file_path': stmt.excluded.file_path,
                        'file_size_bytes': stmt.excluded.file_size_bytes,
                        'last_accessed': stmt.excluded.last_accessed,
                        'access_count': CacheMetadata.access_count + 1
                    }
                )
                
                await session.execute(stmt)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating cache metadata: {e}")
                raise
    
    async def update_cache_access(self, platform: str, user_id: str):
        """Update cache access timestamp and count."""
        async with self.get_session() as session:
            try:
                from sqlalchemy import select
                result = await session.execute(
                    select(CacheMetadata).where(
                        CacheMetadata.platform == platform,
                        CacheMetadata.user_id == user_id
                    )
                )
                cache_metadata = result.scalar_one_or_none()
                
                if cache_metadata:
                    cache_metadata.last_accessed = datetime.utcnow()
                    cache_metadata.access_count += 1
                    await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating cache access: {e}")
    
    async def delete_cache_metadata(self, platform: str, user_id: str):
        """Delete cache metadata."""
        async with self.get_session() as session:
            try:
                from sqlalchemy import delete
                await session.execute(
                    delete(CacheMetadata).where(
                        CacheMetadata.platform == platform,
                        CacheMetadata.user_id == user_id
                    )
                )
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error deleting cache metadata: {e}")
                raise
    
    async def get_statistics(self) -> Dict:
        """Get database statistics."""
        async with self.get_session() as session:
            try:
                from sqlalchemy import select, func
                
                # Total requests
                result = await session.execute(select(func.count(AvatarRequest.id)))
                total_requests = result.scalar() or 0
                
                # Successful requests
                result = await session.execute(
                    select(func.count(AvatarRequest.id)).where(AvatarRequest.success == True)
                )
                successful_requests = result.scalar() or 0
                
                # Cache hits
                result = await session.execute(
                    select(func.count(AvatarRequest.id)).where(AvatarRequest.cache_hit == True)
                )
                cache_hits = result.scalar() or 0
                
                # Platform breakdown
                result = await session.execute(
                    select(AvatarRequest.platform, func.count(AvatarRequest.id))
                    .group_by(AvatarRequest.platform)
                    .order_by(func.count(AvatarRequest.id).desc())
                )
                platform_stats = dict(result.fetchall())
                
                # Cache metadata stats
                result = await session.execute(
                    select(
                        func.count(CacheMetadata.id),
                        func.sum(CacheMetadata.file_size_bytes)
                    )
                )
                cache_result = result.fetchone()
                cached_files = cache_result[0] if cache_result[0] else 0
                cache_size_bytes = cache_result[1] if cache_result[1] else 0
                
                return {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "cache_hits": cache_hits,
                    "cache_hit_rate": round((cache_hits / total_requests) * 100, 2) if total_requests > 0 else 0,
                    "platform_stats": platform_stats,
                    "cached_files": cached_files,
                    "cache_size_mb": round(cache_size_bytes / (1024 * 1024), 2)
                }
            except Exception as e:
                logger.error(f"Error getting statistics: {e}")
                return {}
    
    async def cleanup_old_rate_limit_data(self, hours: int = 24):
        """Clean up old rate limit tracking data."""
        async with self.get_session() as session:
            try:
                from sqlalchemy import delete
                await session.execute(
                    delete(RateLimitTracking).where(
                        RateLimitTracking.request_timestamp < func.now() - text(f"interval '{hours} hours'")
                    )
                )
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error cleaning up rate limit data: {e}")
    
    async def bulk_insert_cache_metadata(self, metadata_list: list):
        """Bulk insert cache metadata for efficient batch operations using UPSERT."""
        async with self.get_session() as session:
            try:
                from sqlalchemy.dialects.postgresql import insert
                
                # Prepare data for bulk upsert
                values_list = [
                    {
                        'platform': item[0],
                        'user_id': item[1],
                        'file_path': item[2],
                        'file_size_bytes': item[3],
                        'created_timestamp': datetime.utcnow(),
                        'last_accessed': datetime.utcnow(),
                        'access_count': 1
                    } for item in metadata_list
                ]
                
                # Use PostgreSQL's ON CONFLICT for bulk upsert
                stmt = insert(CacheMetadata).values(values_list)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['platform', 'user_id'],
                    set_={
                        'file_path': stmt.excluded.file_path,
                        'file_size_bytes': stmt.excluded.file_size_bytes,
                        'last_accessed': stmt.excluded.last_accessed,
                        'access_count': CacheMetadata.access_count + 1
                    }
                )
                
                await session.execute(stmt)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error bulk inserting cache metadata: {e}")
                raise
    
    async def bulk_log_avatar_requests(self, requests_list: list):
        """Bulk log avatar requests for efficient batch operations."""
        async with self.get_session() as session:
            try:
                avatar_request_objects = [
                    AvatarRequest(
                        platform=item[0],
                        user_id=item[1],
                        cache_hit=item[2],
                        success=item[3],
                        error_message=item[4],
                        ip_address=item[5]
                    ) for item in requests_list
                ]
                session.add_all(avatar_request_objects)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error bulk logging avatar requests: {e}")
                raise
    
    async def _update_user_analytics(self, session: AsyncSession, ip_address: str, platform: str, user_agent: Optional[str] = None):
        """Update user analytics for tracking user behavior using UPSERT."""
        try:
            from sqlalchemy.dialects.postgresql import insert
            from sqlalchemy import select
            
            # First try to get existing user to update platforms_used properly
            result = await session.execute(
                select(UserAnalytics).where(UserAnalytics.ip_address == ip_address)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Update existing user
                platforms_used = existing_user.platforms_used or ""
                if platform not in platforms_used:
                    platforms_used += f",{platform}" if platforms_used else platform
                    unique_platforms = len(platforms_used.split(","))
                else:
                    unique_platforms = existing_user.unique_platforms
                
                existing_user.last_seen = datetime.utcnow()
                existing_user.total_requests += 1
                existing_user.unique_platforms = unique_platforms
                existing_user.platforms_used = platforms_used
                existing_user.user_agent = user_agent
            else:
                # Use UPSERT for new user to handle race conditions
                stmt = insert(UserAnalytics).values(
                    ip_address=ip_address,
                    first_seen=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                    total_requests=1,
                    unique_platforms=1,
                    platforms_used=platform,
                    user_agent=user_agent,
                    is_bot=self._is_bot_user_agent(user_agent)
                )
                
                stmt = stmt.on_conflict_do_update(
                    index_elements=['ip_address'],
                    set_={
                        'last_seen': stmt.excluded.last_seen,
                        'total_requests': UserAnalytics.total_requests + 1,
                        'user_agent': stmt.excluded.user_agent
                    }
                )
                
                await session.execute(stmt)
        except Exception as e:
            logger.error(f"Error updating user analytics: {e}")
    
    def _is_bot_user_agent(self, user_agent: Optional[str]) -> bool:
        """Detect if user agent is likely a bot."""
        if not user_agent:
            return False
        
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python-requests']
        return any(indicator in user_agent.lower() for indicator in bot_indicators)
    
    async def _update_daily_stats(self, session: AsyncSession, platform: str, success: bool, cache_hit: bool, response_time_ms: Optional[int]):
        """Update daily statistics."""
        try:
            from sqlalchemy import select
            today = date.today()  # <-- FIX
            
            result = await session.execute(
                select(DailyStats).where(DailyStats.date == today)
            )
            daily_stats = result.scalar_one_or_none()
            
            if daily_stats:
                daily_stats.total_requests += 1
                if cache_hit:
                    daily_stats.cache_hits += 1
                if not success:
                    daily_stats.errors += 1
                
                # Update platform-specific requests
                platform_col = f"{platform}_requests"
                if hasattr(daily_stats, platform_col):
                    setattr(daily_stats, platform_col, getattr(daily_stats, platform_col) + 1)
                
                # Update avg response time
                if response_time_ms:
                    total_requests = daily_stats.total_requests
                    daily_stats.avg_response_time_ms = (
                        (daily_stats.avg_response_time_ms * (total_requests - 1) + response_time_ms) / total_requests
                    )
            else:
                daily_stats = DailyStats(
                    date=today,
                    total_requests=1,
                    cache_hits=1 if cache_hit else 0,
                    errors=0 if success else 1,
                    avg_response_time_ms=response_time_ms or 0.0
                )
                platform_col = f"{platform}_requests"
                if hasattr(daily_stats, platform_col):
                    setattr(daily_stats, platform_col, 1)
                session.add(daily_stats)
        except Exception as e:
            logger.error(f"Error updating daily stats: {e}")
    
    async def _update_hourly_stats(self, session: AsyncSession, success: bool, cache_hit: bool, response_time_ms: Optional[int]):
        """Update hourly statistics."""
        try:
            from sqlalchemy import select
            now = datetime.utcnow()
            hour_key = now.strftime('%Y-%m-%d %H:00:00')
            
            result = await session.execute(
                select(HourlyStats).where(HourlyStats.datetime == hour_key)
            )
            hourly_stats = result.scalar_one_or_none()
            
            if hourly_stats:
                # Update existing stats
                hourly_stats.requests += 1
                if cache_hit:
                    hourly_stats.cache_hits += 1
                if not success:
                    hourly_stats.errors += 1
            else:
                # Create new hourly stats
                hourly_stats = HourlyStats(
                    datetime=hour_key,
                    requests=1,
                    cache_hits=1 if cache_hit else 0,
                    errors=0 if success else 1
                )
                session.add(hourly_stats)
        except Exception as e:
            logger.error(f"Error updating hourly stats: {e}")
    
    async def log_error(self, error_type: str, error_message: str, platform: Optional[str] = None,
                       user_id: Optional[str] = None, ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None, stack_trace: Optional[str] = None):
        """Log an error for tracking and debugging."""
        async with self.get_session() as session:
            try:
                error_log = ErrorLogs(
                    error_type=error_type,
                    error_message=error_message,
                    platform=platform,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    stack_trace=stack_trace
                )
                session.add(error_log)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error logging error: {e}")
    
    async def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics for the admin dashboard (optimized with parallel queries)."""
        async with self.get_session() as session:
            try:
                from sqlalchemy import select, func, text

                # Run queries sequentially (SQLAlchemy async sessions don't support concurrent operations on same session)
                # This is acceptable since we have a 5-minute cache for performance
                async def get_basic_stats():
                    # Inline the get_statistics() logic to use the same session
                    # Total requests
                    result = await session.execute(select(func.count(AvatarRequest.id)))
                    total_requests = result.scalar() or 0

                    # Successful requests
                    result = await session.execute(
                        select(func.count(AvatarRequest.id))
                        .where(AvatarRequest.success == True)
                    )
                    successful_requests = result.scalar() or 0

                    # Cache hits
                    result = await session.execute(
                        select(func.count(AvatarRequest.id))
                        .where(AvatarRequest.cache_hit == True)
                    )
                    cache_hits = result.scalar() or 0

                    # Cache hit rate
                    cache_hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0.0

                    # Cached files
                    result = await session.execute(select(func.count(CacheMetadata.id)))
                    cached_files = result.scalar() or 0

                    # Cache size
                    result = await session.execute(
                        select(func.sum(CacheMetadata.file_size_bytes))
                    )
                    cache_size_bytes = result.scalar() or 0
                    cache_size_mb = (cache_size_bytes / (1024 * 1024)) if cache_size_bytes else 0.0

                    return {
                        "total_requests": total_requests,
                        "successful_requests": successful_requests,
                        "cache_hits": cache_hits,
                        "cache_hit_rate": cache_hit_rate,
                        "cached_files": cached_files,
                        "cache_size_mb": cache_size_mb
                    }
                
                async def get_user_analytics():
                    result = await session.execute(
                        select(
                            func.count(UserAnalytics.id).label('total_users'),
                            func.count().filter(UserAnalytics.is_bot == False).label('human_users'),
                            func.count().filter(UserAnalytics.is_bot == True).label('bot_users'),
                            func.avg(UserAnalytics.total_requests).label('avg_requests_per_user'),
                            func.max(UserAnalytics.total_requests).label('max_requests_per_user')
                        )
                    )
                    return result.first()._asdict()
                
                async def get_recent_activity():
                    result = await session.execute(
                        select(
                            func.count(AvatarRequest.id).label('requests_24h'),
                            func.count(func.distinct(AvatarRequest.ip_address)).label('unique_users_24h'),
                            func.count().filter(AvatarRequest.cache_hit == True).label('cache_hits_24h'),
                            func.count().filter(AvatarRequest.success == False).label('errors_24h')
                        ).where(
                            AvatarRequest.request_timestamp > func.now() - text("interval '24 hours'")
                        )
                    )
                    return result.first()._asdict()
                
                async def get_platform_popularity():
                    result = await session.execute(
                        select(AvatarRequest.platform, func.count(AvatarRequest.id).label('requests'))
                        .where(AvatarRequest.request_timestamp > func.now() - text("interval '7 days'"))
                        .group_by(AvatarRequest.platform)
                        .order_by(func.count(AvatarRequest.id).desc())
                    )
                    return dict(result.fetchall())
                
                async def get_daily_trends():
                    result = await session.execute(
                        select(DailyStats.date, DailyStats.total_requests, DailyStats.unique_users,
                              DailyStats.cache_hits, DailyStats.errors)
                        .where(DailyStats.date >= func.current_date() - text("interval '7 days'"))
                        .order_by(DailyStats.date.desc())
                    )
                    return [row._asdict() for row in result.fetchall()]
                
                async def get_hourly_trends():
                    today_str = datetime.utcnow().strftime('%Y-%m-%d 00:00:00')
                    result = await session.execute(
                        select(HourlyStats.datetime, HourlyStats.requests, HourlyStats.unique_users,
                              HourlyStats.cache_hits, HourlyStats.errors)
                        .where(HourlyStats.datetime >= today_str)
                        .order_by(HourlyStats.datetime)
                    )
                    return [row._asdict() for row in result.fetchall()]
                
                async def get_top_users():
                    result = await session.execute(
                        select(UserAnalytics.ip_address, UserAnalytics.total_requests,
                              UserAnalytics.platforms_used, UserAnalytics.last_seen)
                        .order_by(UserAnalytics.total_requests.desc())
                        .limit(10)
                    )
                    return [row._asdict() for row in result.fetchall()]
                
                async def get_recent_errors():
                    result = await session.execute(
                        select(ErrorLogs.error_type, ErrorLogs.error_message, ErrorLogs.platform,
                              ErrorLogs.timestamp, ErrorLogs.ip_address)
                        .where(ErrorLogs.timestamp > func.now() - text("interval '24 hours'"))
                        .order_by(ErrorLogs.timestamp.desc())
                        .limit(20)
                    )
                    return [row._asdict() for row in result.fetchall()]

                # Execute queries sequentially (SQLAlchemy async sessions don't support concurrent operations)
                # This is acceptable since we have a 5-minute cache
                basic_stats = await get_basic_stats()
                user_stats = await get_user_analytics()
                recent_stats = await get_recent_activity()
                platform_popularity = await get_platform_popularity()
                daily_trends = await get_daily_trends()
                hourly_trends = await get_hourly_trends()
                top_users = await get_top_users()
                recent_errors = await get_recent_errors()

                return {
                    **basic_stats,
                    "user_analytics": user_stats,
                    "recent_activity": recent_stats,
                    "platform_popularity": platform_popularity,
                    "daily_trends": daily_trends,
                    "hourly_trends": hourly_trends,
                    "top_users": top_users,
                    "recent_errors": recent_errors
                }
            except Exception as e:
                logger.error(f"Error getting comprehensive stats: {e}")
                return {}

    
    async def close(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")
