import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest
from ...config.settings import settings
from ...monitoring.logger import get_logger
from ...database import SessionLocal
from ...models.system_metric import SystemMetric

logger = get_logger(__name__)

class MetricsCollector:
    """Metrics collector for system monitoring"""
    
    def __init__(self):
        # Prometheus metrics
        self.query_counter = Counter(
            'rag_queries_total',
            'Total number of queries processed',
            ['status', 'type']
        )
        
        self.action_counter = Counter(
            'rag_actions_total',
            'Total number of actions executed',
            ['action_type', 'status']
        )
        
        self.response_time = Histogram(
            'rag_response_time_seconds',
            'Response time for queries',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.data_points_counter = Counter(
            'rag_data_points_total',
            'Total number of data points processed',
            ['data_type']
        )
        
        self.error_counter = Counter(
            'rag_errors_total',
            'Total number of errors',
            ['error_type', 'component']
        )
        
        self.active_streams = Gauge(
            'rag_active_streams',
            'Number of active data streams'
        )
        
        self.system_health = Gauge(
            'rag_system_health',
            'System health score (0-1)'
        )
        
        self.memory_usage = Gauge(
            'rag_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        # Internal metrics storage
        self.metrics_buffer = []
        self.buffer_size = 100
        self.last_flush = datetime.utcnow()
        self.flush_interval = 60  # seconds
        
        # Statistics
        self.stats = defaultdict(lambda: defaultdict(int))
        
    def record_query(self, query_type: str, status: str, duration: float):
        """Record a query"""
        self.query_counter.labels(status=status, type=query_type).inc()
        
        self.response_time.observe(duration)
        
        # Store in buffer
        self.metrics_buffer.append({
            "metric_name": "query",
            "metric_value": 1,
            "metadata": {
                "type": query_type,
                "status": status,
                "duration": duration
            },
            "timestamp": datetime.utcnow()
        })
        
        # Update stats
        self.stats["queries"]["total"] += 1
        self.stats["queries"][f"status_{status}"] += 1
        self.stats["queries"][f"type_{query_type}"] += 1
        
        self._check_flush()
    
    def record_action(self, action_type: str, status: str):
        """Record an action"""
        self.action_counter.labels(action_type=action_type, status=status).inc()
        
        self.metrics_buffer.append({
            "metric_name": "action",
            "metric_value": 1,
            "metadata": {
                "action_type": action_type,
                "status": status
            },
            "timestamp": datetime.utcnow()
        })
        
        self.stats["actions"]["total"] += 1
        self.stats["actions"][f"type_{action_type}"] += 1
        self.stats["actions"][f"status_{status}"] += 1
        
        self._check_flush()
    
    def record_data_point(self, data_type: str, count: int = 1):
        """Record data points"""
        self.data_points_counter.labels(data_type=data_type).inc(count)
        
        self.metrics_buffer.append({
            "metric_name": "data_points_processed",
            "metric_value": count,
            "metadata": {
                "data_type": data_type
            },
            "timestamp": datetime.utcnow()
        })
        
        self.stats["data_points"]["total"] += count
        self.stats["data_points"][f"type_{data_type}"] += count
        
        self._check_flush()
    
    def record_error(self, error_type: str, component: str, message: str = ""):
        """Record an error"""
        self.error_counter.labels(error_type=error_type, component=component).inc()
        
        self.metrics_buffer.append({
            "metric_name": "error",
            "metric_value": 1,
            "metadata": {
                "error_type": error_type,
                "component": component,
                "message": message[:200]  # Truncate long messages
            },
            "timestamp": datetime.utcnow()
        })
        
        self.stats["errors"]["total"] += 1
        self.stats["errors"][f"type_{error_type}"] += 1
        self.stats["errors"][f"component_{component}"] += 1
        
        self._check_flush()
    
    def set_active_streams(self, count: int):
        """Set number of active streams"""
        self.active_streams.set(count)
        
        self.metrics_buffer.append({
            "metric_name": "active_streams",
            "metric_value": count,
            "timestamp": datetime.utcnow()
        })
        
        self._check_flush()
    
    def set_system_health(self, score: float):
        """Set system health score"""
        self.system_health.set(score)
        
        self.metrics_buffer.append({
            "metric_name": "system_health",
            "metric_value": score,
            "timestamp": datetime.utcnow()
        })
        
        self._check_flush()
    
    def set_memory_usage(self, bytes_used: int):
        """Set memory usage"""
        self.memory_usage.set(bytes_used)
        
        self.metrics_buffer.append({
            "metric_name": "memory_usage_bytes",
            "metric_value": bytes_used,
            "timestamp": datetime.utcnow()
        })
        
        self._check_flush()
    
    def record_custom_metric(self, name: str, value: float, metadata: Dict[str, Any] = None):
        """Record a custom metric"""
        self.metrics_buffer.append({
            "metric_name": name,
            "metric_value": value,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        })
        
        self._check_flush()
    
    def _check_flush(self):
        """Check if metrics should be flushed to database"""
        now = datetime.utcnow()
        
        if (len(self.metrics_buffer) >= self.buffer_size or 
            (now - self.last_flush).total_seconds() >= self.flush_interval):
            asyncio.create_task(self._flush_metrics())
    
    async def _flush_metrics(self):
        """Flush metrics to database"""
        if not self.metrics_buffer:
            return
        
        try:
            db = SessionLocal()
            
            # Convert buffer to database models
            metrics_to_save = []
            for metric_data in self.metrics_buffer:
                metric = SystemMetric(
                    metric_name=metric_data["metric_name"],
                    metric_value=metric_data["metric_value"],
                    metadata=metric_data.get("metadata", {}),
                    timestamp=metric_data["timestamp"]
                )
                metrics_to_save.append(metric)
            
            # Bulk insert
            db.bulk_save_objects(metrics_to_save)
            db.commit()
            
            logger.info(f"Flushed {len(metrics_to_save)} metrics to database")
            
            # Clear buffer
            self.metrics_buffer.clear()
            self.last_flush = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to flush metrics: {e}")
            # Keep metrics in buffer for retry
        finally:
            db.close()
    
    def get_prometheus_metrics(self) -> bytes:
        """Get Prometheus metrics in text format"""
        return generate_latest()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        stats = dict(self.stats)
        
        # Add timestamp
        stats["timestamp"] = datetime.utcnow().isoformat()
        
        # Add buffer info
        stats["metrics_buffer_size"] = len(self.metrics_buffer)
        stats["last_flush"] = self.last_flush.isoformat()
        
        return stats
    
    def get_metric_summary(self, metric_name: str, 
                          time_range: str = "1h") -> Dict[str, Any]:
        """Get summary for a specific metric"""
        try:
            db = SessionLocal()
            
            # Calculate time range
            now = datetime.utcnow()
            if time_range == "1h":
                start_time = now - timedelta(hours=1)
            elif time_range == "24h":
                start_time = now - timedelta(hours=24)
            elif time_range == "7d":
                start_time = now - timedelta(days=7)
            else:
                start_time = now - timedelta(hours=1)
            
            # Query metrics
            metrics = db.query(SystemMetric).filter(
                SystemMetric.metric_name == metric_name,
                SystemMetric.timestamp >= start_time
            ).order_by(SystemMetric.timestamp).all()
            
            if not metrics:
                return {
                    "metric_name": metric_name,
                    "time_range": time_range,
                    "count": 0,
                    "data": []
                }
            
            # Calculate statistics
            values = [m.metric_value for m in metrics]
            
            summary = {
                "metric_name": metric_name,
                "time_range": time_range,
                "count": len(metrics),
                "total": sum(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "data": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "value": m.metric_value,
                        "metadata": m.metadata
                    }
                    for m in metrics[-100:]  # Limit to 100 data points
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metric summary: {e}")
            return {
                "metric_name": metric_name,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def start_periodic_flush(self, interval: int = 60):
        """Start periodic metric flushing"""
        while True:
            try:
                await self._flush_metrics()
            except Exception as e:
                logger.error(f"Periodic flush error: {e}")
            
            await asyncio.sleep(interval)
    
    def create_timer(self, name: str) -> Callable:
        """Create a timer context manager"""
        class Timer:
            def __init__(self, collector, name):
                self.collector = collector
                self.name = name
                self.start_time = None
            
            def __enter__(self):
                self.start_time = time.time()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time
                
                if exc_type:
                    status = "error"
                    error_type = exc_type.__name__
                    self.collector.record_error(
                        error_type=error_type,
                        component=self.name,
                        message=str(exc_val)
                    )
                else:
                    status = "success"
                
                self.collector.record_custom_metric(
                    name=f"{self.name}_duration",
                    value=duration,
                    metadata={"status": status}
                )
        
        return Timer(self, name)


# Global metrics collector instance
metrics_collector = MetricsCollector()