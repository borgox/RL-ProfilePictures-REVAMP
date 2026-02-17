import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Tuple
from pydantic import BaseModel
from database.models import Database
from config import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Statistics"])
database: Optional[Database] = None

# In-memory cache for stats dashboard (TTL: 5 minutes)
_stats_cache: Optional[Tuple[Dict, datetime]] = None
_cache_ttl = timedelta(minutes=5)

async def get_database() -> Database:
    if database is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return database


def verify_admin_secret(request: Request):
    secret = request.query_params.get("secret")
    if secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Invalid admin secret")
    return True


@router.get("/stats", response_class=HTMLResponse)
async def get_stats_dashboard(
    request: Request,
    db: Database = Depends(get_database),
    _: bool = Depends(verify_admin_secret)
):
    """
    Get admin statistics dashboard with caching for performance.
    Cache expires after 5 minutes.
    """
    global _stats_cache
    
    try:
        # Check cache
        if _stats_cache is not None:
            cached_stats, cache_time = _stats_cache
            if datetime.utcnow() - cache_time < _cache_ttl:
                logger.debug("Returning cached stats dashboard")
                html_content = generate_dashboard_html(cached_stats)
                return HTMLResponse(content=html_content)
        
        # Fetch fresh stats
        stats = await db.get_comprehensive_stats()
        
        # Update cache
        _stats_cache = (stats, datetime.utcnow())
        logger.debug("Stats cache updated")
        
        html_content = generate_dashboard_html(stats)
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error generating stats dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate dashboard")


@router.post("/stats/clear-cache")
async def clear_stats_cache(
    request: Request,
    _: bool = Depends(verify_admin_secret)
):
    """Clear the stats dashboard cache (admin only)."""
    global _stats_cache
    _stats_cache = None
    logger.info("Stats cache cleared")
    return {"success": True, "message": "Cache cleared"}

def generate_dashboard_html(stats: dict) -> str:
    basic_stats = {
        "total_requests": stats.get("total_requests", 0),
        "successful_requests": stats.get("successful_requests", 0),
        "cache_hits": stats.get("cache_hits", 0),
        "cache_hit_rate": stats.get("cache_hit_rate", 0),
        "cached_files": stats.get("cached_files", 0),
        "cache_size_mb": stats.get("cache_size_mb", 0)
    }

    user_analytics = stats.get("user_analytics", {})
    recent_activity = stats.get("recent_activity", {})
    platform_popularity = stats.get("platform_popularity", {})
    daily_trends = stats.get("daily_trends", [])
    hourly_trends = stats.get("hourly_trends", [])
    top_users = stats.get("top_users", [])
    recent_errors = stats.get("recent_errors", [])

    # --- Prevent division by zero ---
    total_requests = basic_stats["total_requests"]
    successful_requests = basic_stats["successful_requests"]
    success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0.0

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RLProfilePicturesREVAMP Analytics Dashboard</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                background-attachment: fixed;
                min-height: 100vh;
                color: #333;
                animation: fadeIn 0.5s ease-in;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            
            @keyframes slideUp {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                color: white;
                animation: slideUp 0.6s ease-out;
            }}
            
            .header h1 {{
                font-size: 3rem;
                margin-bottom: 15px;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
                font-weight: 700;
                letter-spacing: -1px;
                background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .header p {{
                font-size: 1.2rem;
                opacity: 0.95;
                font-weight: 300;
                letter-spacing: 0.5px;
            }}
            
            .cache-indicator {{
                display: inline-block;
                margin-top: 10px;
                padding: 6px 12px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                font-size: 0.85rem;
                backdrop-filter: blur(10px);
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .stat-card {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                border-left: 5px solid;
                position: relative;
                overflow: hidden;
                animation: slideUp 0.6s ease-out;
                animation-fill-mode: both;
            }}
            
            .stat-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
                opacity: 0;
                transition: opacity 0.3s;
            }}
            
            .stat-card:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            }}
            
            .stat-card:hover::before {{
                opacity: 1;
            }}
            
            .stat-card:nth-child(1) {{ animation-delay: 0.1s; }}
            .stat-card:nth-child(2) {{ animation-delay: 0.2s; }}
            .stat-card:nth-child(3) {{ animation-delay: 0.3s; }}
            .stat-card:nth-child(4) {{ animation-delay: 0.4s; }}
            .stat-card:nth-child(5) {{ animation-delay: 0.5s; }}
            .stat-card:nth-child(6) {{ animation-delay: 0.6s; }}
            
            .stat-card.primary {{ border-left-color: #4CAF50; }}
            .stat-card.success {{ border-left-color: #2196F3; }}
            .stat-card.warning {{ border-left-color: #FF9800; }}
            .stat-card.danger {{ border-left-color: #F44336; }}
            .stat-card.info {{ border-left-color: #9C27B0; }}
            
            .stat-title {{
                font-size: 0.9rem;
                color: #666;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .stat-value {{
                font-size: 3rem;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 8px;
                line-height: 1.2;
            }}
            
            .stat-subtitle {{
                font-size: 0.8rem;
                color: #888;
            }}
            
            .charts-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .chart-container {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                animation: slideUp 0.8s ease-out;
            }}
            
            .chart-container:hover {{
                transform: translateY(-4px);
                box-shadow: 0 16px 48px rgba(0,0,0,0.15);
            }}
            
            .chart-title {{
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 20px;
                color: #333;
                text-align: center;
            }}
            
            .data-table {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                margin-bottom: 25px;
                animation: slideUp 1s ease-out;
                transition: transform 0.3s ease;
            }}
            
            .data-table:hover {{
                transform: translateY(-2px);
            }}
            
            .table-title {{
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 15px;
                color: #333;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }}
            
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
                color: #555;
            }}
            
            tr:hover {{
                background-color: #f8f9fa;
            }}
            
            .platform-badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: bold;
                text-transform: uppercase;
            }}
            
            .platform-steam {{ background: #1b2838; color: white; }}
            .platform-xbox {{ background: #107c10; color: white; }}
            .platform-psn {{ background: #003791; color: white; }}
            .platform-switch {{ background: #e60012; color: white; }}
            .platform-epic {{ background: #0078f2; color: white; }}
            
            .error-item {{
                background: #fff5f5;
                border-left: 4px solid #f44336;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 4px;
            }}
            
            .error-type {{
                font-weight: bold;
                color: #d32f2f;
            }}
            
            .error-message {{
                color: #666;
                font-size: 0.9rem;
            }}
            
            .refresh-btn {{
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                border: none;
                border-radius: 50%;
                width: 65px;
                height: 65px;
                font-size: 1.6rem;
                cursor: pointer;
                box-shadow: 0 8px 24px rgba(76, 175, 80, 0.4);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                z-index: 1000;
                animation: pulse 2s infinite;
            }}
            
            .refresh-btn:hover {{
                transform: scale(1.15) rotate(90deg);
                box-shadow: 0 12px 32px rgba(76, 175, 80, 0.5);
            }}
            
            .refresh-btn:active {{
                transform: scale(1.05) rotate(180deg);
            }}
            
            @media (max-width: 768px) {{
                .charts-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .stats-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎮 RLProfilePicturesREVAMP Analytics</h1>
                <p>Comprehensive tracking and monitoring dashboard</p>
                <div class="cache-indicator">⚡ Real-time Data</div>
            </div>
            
            <!-- Key Metrics -->
            <div class="stats-grid">
                <div class="stat-card primary">
                    <div class="stat-title">Total Requests</div>
                    <div class="stat-value">{basic_stats['total_requests']:,}</div>
                    <div class="stat-subtitle">All time</div>
                </div>
                
                <div class="stat-card success">
                    <div class="stat-title">Success Rate</div>
                    <div class="stat-value">{((basic_stats['successful_requests'] / basic_stats['total_requests']) * 100):.1f}%</div>
                    <div class="stat-subtitle">{basic_stats['successful_requests']:,} successful</div>
                </div>
                
                <div class="stat-card info">
                    <div class="stat-title">Cache Hit Rate</div>
                    <div class="stat-value">{basic_stats['cache_hit_rate']:.1f}%</div>
                    <div class="stat-subtitle">{basic_stats['cache_hits']:,} cache hits</div>
                </div>
                
                <div class="stat-card warning">
                    <div class="stat-title">Cached Files</div>
                    <div class="stat-value">{basic_stats['cached_files']:,}</div>
                    <div class="stat-subtitle">{basic_stats['cache_size_mb']:.1f} MB total</div>
                </div>
                
                <div class="stat-card primary">
                    <div class="stat-title">Unique Users</div>
                    <div class="stat-value">{user_analytics.get('total_users', 0):,}</div>
                    <div class="stat-subtitle">{user_analytics.get('human_users', 0):,} human, {user_analytics.get('bot_users', 0):,} bots</div>
                </div>
                
                <div class="stat-card danger">
                    <div class="stat-title">24h Requests</div>
                    <div class="stat-value">{recent_activity.get('requests_24h', 0):,}</div>
                    <div class="stat-subtitle">{recent_activity.get('unique_users_24h', 0):,} unique users</div>
                </div>
            </div>
            
            <!-- Charts -->
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">Platform Popularity (7 days)</div>
                    <canvas id="platformChart"></canvas>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Daily Request Trends</div>
                    <canvas id="dailyChart"></canvas>
                </div>
            </div>
            
            <!-- Data Tables -->
            <div class="data-table">
                <div class="table-title">Top Users by Request Count</div>
                <table>
                    <thead>
                        <tr>
                            <th>IP Address</th>
                            <th>Total Requests</th>
                            <th>Platforms Used</th>
                            <th>Last Seen</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td>{user.get('ip_address', 'N/A')}</td>
                            <td>{user.get('total_requests', 0):,}</td>
                            <td>{user.get('platforms_used', 'N/A')}</td>
                            <td>{user.get('last_seen', 'N/A')}</td>
                        </tr>
                        ''' for user in top_users[:10]])}
                    </tbody>
                </table>
            </div>
            
            <div class="data-table">
                <div class="table-title">Recent Errors (24h)</div>
                {''.join([f'''
                <div class="error-item">
                    <div class="error-type">{error.get('error_type', 'Unknown')}</div>
                    <div class="error-message">{error.get('error_message', 'No message')}</div>
                    <div style="font-size: 0.8rem; color: #999; margin-top: 5px;">
                        {error.get('platform', 'N/A')} | {error.get('timestamp', 'N/A')} | {error.get('ip_address', 'N/A')}
                    </div>
                </div>
                ''' for error in recent_errors[:10]])}
            </div>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()" title="Refresh Data">🔄</button>
        
        <script>
            // Platform popularity chart
            const platformData = {platform_popularity};
            const platformCtx = document.getElementById('platformChart').getContext('2d');
            new Chart(platformCtx, {{
                type: 'doughnut',
                data: {{
                    labels: Object.keys(platformData),
                    datasets: [{{
                        data: Object.values(platformData),
                        backgroundColor: [
                            '#1b2838', '#107c10', '#003791', '#e60012', '#0078f2'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            
            // Daily trends chart
            const dailyData = {daily_trends};
            const dailyCtx = document.getElementById('dailyChart').getContext('2d');
            new Chart(dailyCtx, {{
                type: 'line',
                data: {{
                    labels: dailyData.map(d => d.date).reverse(),
                    datasets: [{{
                        label: 'Requests',
                        data: dailyData.map(d => d.total_requests).reverse(),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """


class HeartbeatRequest(BaseModel):
    """Request model for heartbeat."""
    platform: str
    user_id: str
    status: str = "online"


class HeartbeatResponse(BaseModel):
    """Response model for heartbeat."""
    success: bool


@router.post("/stats/heartbeat", response_model=HeartbeatResponse)
async def post_heartbeat(
    request_data: HeartbeatRequest,
    request: Request,
    db: Database = Depends(get_database)
):
    """
    Update user heartbeat for statistics tracking.
    
    This endpoint is called periodically by clients to indicate they are online.
    """
    try:
        platform = request_data.platform.lower()
        valid_platforms = ["epic", "steam", "psn", "xbox", "switch"]
        if platform not in valid_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
            )
        
        status = request_data.status.lower()
        if status not in ["online", "offline"]:
            status = "online"
        
        await db.update_user_heartbeat(platform, request_data.user_id, status)
        
        logger.debug(f"Heartbeat updated for {platform} user {request_data.user_id}: {status}")
        return HeartbeatResponse(success=True)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing heartbeat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/summary")
async def get_statistics_summary(
    request: Request,
    db: Database = Depends(get_database)
):
    """
    Get statistics summary (total, online, offline users).
    
    This endpoint is optimized with database queries and should be fast.
    Consider adding caching layer for high-traffic scenarios.
    """
    try:
        stats = await db.get_statistics_summary()
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")