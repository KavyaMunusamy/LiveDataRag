import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from ...config.settings import settings
from ...monitoring.logger import get_logger
from ...database import SessionLocal
from ...models.action_log import ActionLog
from ...models.system_metric import SystemMetric

logger = get_logger(__name__)

class DashboardService:
    """Dashboard service for system monitoring and visualization"""
    
    def __init__(self):
        self.metrics_cache = {}
        self.cache_ttl = 30  # seconds
        self.last_update = {}
        
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get system overview dashboard data"""
        cache_key = "system_overview"
        cached = self._get_cached(cache_key)
        
        if cached:
            return cached
        
        try:
            db = SessionLocal()
            
            # Get recent metrics
            recent_metrics = db.query(SystemMetric).order_by(
                SystemMetric.timestamp.desc()
            ).limit(100).all()
            
            # Get action statistics
            action_stats = await self._get_action_stats(db)
            
            # Get data pipeline status
            pipeline_status = await self._get_pipeline_status(db)
            
            # Calculate system health
            system_health = self._calculate_system_health(recent_metrics)
            
            # Compile dashboard data
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_health": system_health,
                "metrics": {
                    "last_hour": await self._get_metrics_for_period("1h"),
                    "last_24h": await self._get_metrics_for_period("24h"),
                    "last_7d": await self._get_metrics_for_period("7d")
                },
                "actions": action_stats,
                "data_pipeline": pipeline_status,
                "alerts": await self._get_recent_alerts(db),
                "performance": await self._get_performance_metrics(db)
            }
            
            # Cache the result
            self._set_cached(cache_key, dashboard_data)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting system overview: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "system_health": {"status": "unknown", "score": 0}
            }
        finally:
            db.close()
    
    async def _get_action_stats(self, db) -> Dict[str, Any]:
        """Get action execution statistics"""
        # Get counts by status
        status_counts = db.query(
            ActionLog.status,
            db.func.count(ActionLog.id)
        ).group_by(ActionLog.status).all()
        
        # Get counts by type
        type_counts = db.query(
            ActionLog.action_type,
            db.func.count(ActionLog.id)
        ).group_by(ActionLog.action_type).all()
        
        # Get recent actions
        recent_actions = db.query(ActionLog).order_by(
            ActionLog.timestamp.desc()
        ).limit(10).all()
        
        # Calculate success rate
        total_actions = sum(count for _, count in status_counts)
        successful_actions = sum(
            count for status, count in status_counts 
            if status == "executed"
        )
        
        success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
        
        return {
            "total_actions": total_actions,
            "success_rate": round(success_rate, 2),
            "by_status": dict(status_counts),
            "by_type": dict(type_counts),
            "recent_actions": [
                {
                    "id": action.id,
                    "type": action.action_type,
                    "status": action.status,
                    "timestamp": action.timestamp.isoformat(),
                    "reason": action.reason
                }
                for action in recent_actions
            ]
        }
    
    async def _get_pipeline_status(self, db) -> Dict[str, Any]:
        """Get data pipeline status"""
        # Get recent data points
        recent_data = db.query(SystemMetric).filter(
            SystemMetric.metric_name == "data_points_processed"
        ).order_by(SystemMetric.timestamp.desc()).limit(10).all()
        
        # Calculate throughput
        if len(recent_data) >= 2:
            latest = recent_data[0]
            previous = recent_data[-1]
            
            time_diff = (latest.timestamp - previous.timestamp).total_seconds()
            value_diff = latest.metric_value - previous.metric_value
            
            if time_diff > 0:
                throughput = value_diff / time_diff
            else:
                throughput = 0
        else:
            throughput = 0
        
        # Get error rate
        error_metrics = db.query(SystemMetric).filter(
            SystemMetric.metric_name == "processing_errors"
        ).order_by(SystemMetric.timestamp.desc()).limit(10).all()
        
        total_errors = sum(metric.metric_value for metric in error_metrics)
        
        return {
            "throughput_per_second": round(throughput, 2),
            "total_errors": total_errors,
            "data_points_today": await self._get_today_metric("data_points_processed"),
            "active_streams": await self._get_active_streams_count()
        }
    
    async def _get_metrics_for_period(self, period: str) -> Dict[str, Any]:
        """Get metrics for a specific time period"""
        # Define time ranges
        now = datetime.utcnow()
        
        if period == "1h":
            start_time = now - timedelta(hours=1)
            interval = "1m"
        elif period == "24h":
            start_time = now - timedelta(hours=24)
            interval = "1h"
        elif period == "7d":
            start_time = now - timedelta(days=7)
            interval = "1d"
        else:
            start_time = now - timedelta(hours=1)
            interval = "1m"
        
        try:
            db = SessionLocal()
            
            # Get metrics for the period
            metrics = db.query(SystemMetric).filter(
                SystemMetric.timestamp >= start_time
            ).order_by(SystemMetric.timestamp).all()
            
            # Group by metric name and interval
            grouped_metrics = {}
            
            for metric in metrics:
                metric_name = metric.metric_name
                if metric_name not in grouped_metrics:
                    grouped_metrics[metric_name] = []
                
                grouped_metrics[metric_name].append({
                    "timestamp": metric.timestamp.isoformat(),
                    "value": metric.metric_value,
                    "metadata": metric.metadata
                })
            
            # Process for charting
            chart_data = {}
            for metric_name, data_points in grouped_metrics.items():
                # Aggregate by interval
                if interval == "1m":
                    chart_data[metric_name] = data_points[-60:]  # Last 60 minutes
                elif interval == "1h":
                    # Group by hour
                    hourly_data = {}
                    for point in data_points:
                        hour_key = point["timestamp"][:13] + ":00:00"
                        if hour_key not in hourly_data:
                            hourly_data[hour_key] = []
                        hourly_data[hour_key].append(point["value"])
                    
                    chart_data[metric_name] = [
                        {
                            "timestamp": hour,
                            "value": sum(values) / len(values) if values else 0
                        }
                        for hour, values in hourly_data.items()
                    ]
                elif interval == "1d":
                    # Group by day
                    daily_data = {}
                    for point in data_points:
                        day_key = point["timestamp"][:10]
                        if day_key not in daily_data:
                            daily_data[day_key] = []
                        daily_data[day_key].append(point["value"])
                    
                    chart_data[metric_name] = [
                        {
                            "timestamp": day + "T00:00:00",
                            "value": sum(values) / len(values) if values else 0
                        }
                        for day, values in daily_data.items()
                    ]
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error getting metrics for period {period}: {e}")
            return {}
        finally:
            db.close()
    
    def _calculate_system_health(self, metrics: List[SystemMetric]) -> Dict[str, Any]:
        """Calculate overall system health score"""
        if not metrics:
            return {"status": "unknown", "score": 0, "components": {}}
        
        # Component weights
        weights = {
            "api_health": 0.3,
            "database_health": 0.25,
            "processing_health": 0.25,
            "action_health": 0.2
        }
        
        component_scores = {}
        total_score = 0
        
        # Calculate component scores
        for component, weight in weights.items():
            # Get relevant metrics
            component_metrics = [
                m for m in metrics 
                if m.metric_name.startswith(component.replace("_health", ""))
            ]
            
            if component_metrics:
                # Average the last 5 values
                recent_values = [m.metric_value for m in component_metrics[-5:]]
                avg_score = sum(recent_values) / len(recent_values)
                component_scores[component] = avg_score
                total_score += avg_score * weight
            else:
                component_scores[component] = 0
        
        # Determine status
        if total_score >= 0.9:
            status = "excellent"
        elif total_score >= 0.7:
            status = "good"
        elif total_score >= 0.5:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "status": status,
            "score": round(total_score, 3),
            "components": component_scores,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_recent_alerts(self, db) -> List[Dict[str, Any]]:
        """Get recent system alerts"""
        # Get alert metrics
        alerts = db.query(SystemMetric).filter(
            SystemMetric.metric_name == "system_alert"
        ).order_by(SystemMetric.timestamp.desc()).limit(20).all()
        
        return [
            {
                "level": metric.metadata.get("level", "info"),
                "message": metric.metadata.get("message", ""),
                "timestamp": metric.timestamp.isoformat(),
                "component": metric.metadata.get("component", "unknown")
            }
            for metric in alerts
        ]
    
    async def _get_performance_metrics(self, db) -> Dict[str, Any]:
        """Get performance metrics"""
        # Get response time metrics
        response_times = db.query(SystemMetric).filter(
            SystemMetric.metric_name == "response_time_ms"
        ).order_by(SystemMetric.timestamp.desc()).limit(100).all()
        
        if response_times:
            avg_response_time = sum(
                m.metric_value for m in response_times
            ) / len(response_times)
            
            # Get percentiles
            values = sorted([m.metric_value for m in response_times])
            p95 = values[int(len(values) * 0.95)] if len(values) > 0 else 0
            p99 = values[int(len(values) * 0.99)] if len(values) > 0 else 0
        else:
            avg_response_time = 0
            p95 = 0
            p99 = 0
        
        return {
            "avg_response_time_ms": round(avg_response_time, 2),
            "p95_response_time_ms": round(p95, 2),
            "p99_response_time_ms": round(p99, 2),
            "queries_per_second": await self._get_qps(),
            "error_rate": await self._get_error_rate()
        }
    
    async def _get_today_metric(self, metric_name: str) -> float:
        """Get today's total for a metric"""
        try:
            db = SessionLocal()
            
            today_start = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            
            result = db.query(db.func.sum(SystemMetric.metric_value)).filter(
                SystemMetric.metric_name == metric_name,
                SystemMetric.timestamp >= today_start
            ).scalar()
            
            return result or 0
            
        except Exception as e:
            logger.error(f"Error getting today metric {metric_name}: {e}")
            return 0
        finally:
            db.close()
    
    async def _get_active_streams_count(self) -> int:
        """Get count of active data streams"""
        # This would query your stream manager
        # For now, return mock value
        return 3
    
    async def _get_qps(self) -> float:
        """Get queries per second"""
        try:
            db = SessionLocal()
            
            # Get query count from last minute
            one_min_ago = datetime.utcnow() - timedelta(minutes=1)
            
            count = db.query(db.func.count(SystemMetric.id)).filter(
                SystemMetric.metric_name == "query_count",
                SystemMetric.timestamp >= one_min_ago
            ).scalar()
            
            return count or 0
            
        except Exception as e:
            logger.error(f"Error getting QPS: {e}")
            return 0
        finally:
            db.close()
    
    async def _get_error_rate(self) -> float:
        """Get error rate percentage"""
        try:
            db = SessionLocal()
            
            # Get error count from last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            error_count = db.query(db.func.sum(SystemMetric.metric_value)).filter(
                SystemMetric.metric_name == "processing_errors",
                SystemMetric.timestamp >= one_hour_ago
            ).scalar() or 0
            
            total_operations = db.query(db.func.sum(SystemMetric.metric_value)).filter(
                SystemMetric.metric_name == "data_points_processed",
                SystemMetric.timestamp >= one_hour_ago
            ).scalar() or 0
            
            if total_operations > 0:
                return (error_count / total_operations) * 100
            else:
                return 0
            
        except Exception as e:
            logger.error(f"Error getting error rate: {e}")
            return 0
        finally:
            db.close()
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data"""
        if key in self.metrics_cache:
            data, timestamp = self.metrics_cache[key]
            if datetime.utcnow() - timestamp < timedelta(seconds=self.cache_ttl):
                return data
        return None
    
    def _set_cached(self, key: str, data: Any):
        """Set cached data"""
        self.metrics_cache[key] = (data, datetime.utcnow())
        
        # Clean old cache entries
        self._clean_cache()
    
    def _clean_cache(self):
        """Clean old cache entries"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.cache_ttl * 2)
        
        to_remove = []
        for key, (_, timestamp) in self.metrics_cache.items():
            if timestamp < cutoff:
                to_remove.append(key)
        
        for key in to_remove:
            del self.metrics_cache[key]
    
    async def get_real_time_updates(self) -> Dict[str, Any]:
        """Get real-time updates for dashboard"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": await self._get_current_health(),
            "active_alerts": await self._get_active_alerts(),
            "performance": {
                "cpu_usage": await self._get_cpu_usage(),
                "memory_usage": await self._get_memory_usage(),
                "disk_usage": await self._get_disk_usage()
            }
        }
    
    async def _get_current_health(self) -> Dict[str, Any]:
        """Get current health status"""
        # Mock implementation - integrate with actual health checks
        return {
            "status": "healthy",
            "score": 0.95,
            "last_check": datetime.utcnow().isoformat(),
            "components": {
                "api": "healthy",
                "database": "healthy",
                "processing": "healthy",
                "actions": "healthy"
            }
        }
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        # Mock implementation
        return []
    
    async def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        import psutil
        return psutil.cpu_percent(interval=1)
    
    async def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        import psutil
        return psutil.virtual_memory().percent
    
    async def _get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        import psutil
        return psutil.disk_usage('/').percent
    
    async def export_dashboard_data(self, format: str = "json") -> Any:
        """Export dashboard data in specified format"""
        data = await self.get_system_overview()
        
        if format == "json":
            return json.dumps(data, indent=2)
        elif format == "csv":
            # Convert to CSV format (simplified)
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(["Metric", "Value", "Timestamp"])
            
            # Flatten data
            flat_data = self._flatten_dict(data)
            for key, value in flat_data.items():
                if isinstance(value, (str, int, float, bool)):
                    writer.writerow([key, value, datetime.utcnow().isoformat()])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(
                            self._flatten_dict(item, f"{new_key}[{i}]").items()
                        )
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, v))
        
        return dict(items)