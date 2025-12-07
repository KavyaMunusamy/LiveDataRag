from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ...config.settings import settings
from ...monitoring.logger import get_logger

logger = get_logger(__name__)

class TemporalContextManager:
    """Manager for temporal context in RAG system"""
    
    def __init__(self):
        self.time_windows = self._define_time_windows()
        self.seasonal_patterns = self._load_seasonal_patterns()
        self.temporal_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def _define_time_windows(self) -> Dict[str, timedelta]:
        """Define time windows for different contexts"""
        return {
            "realtime": timedelta(minutes=5),
            "very_recent": timedelta(hours=1),
            "recent": timedelta(hours=6),
            "today": timedelta(hours=24),
            "this_week": timedelta(days=7),
            "this_month": timedelta(days=30),
            "historical": timedelta(days=365)
        }
    
    def _load_seasonal_patterns(self) -> Dict[str, Any]:
        """Load seasonal patterns for different data types"""
        return {
            "financial": {
                "trading_hours": {
                    "weekday": {"start": "09:30", "end": "16:00", "timezone": "America/New_York"},
                    "closed": ["SAT", "SUN"]
                },
                "earnings_season": {
                    "quarters": ["Q1", "Q2", "Q3", "Q4"],
                    "typical_months": [1, 4, 7, 10]
                }
            },
            "news": {
                "peak_hours": ["09:00-12:00", "14:00-17:00"],
                "slow_hours": ["00:00-06:00"]
            },
            "social_media": {
                "peak_hours": ["12:00-14:00", "19:00-22:00"],
                "weekend_activity": 1.5  # Weekend multiplier
            }
        }
    
    def analyze_temporal_context(self, 
                                query: str, 
                                data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal context of data points"""
        if not data_points:
            return {"error": "No data points provided"}
        
        # Extract timestamps
        timestamps = []
        for point in data_points:
            ts = self._extract_timestamp(point)
            if ts:
                timestamps.append(ts)
        
        if not timestamps:
            return {"error": "No valid timestamps found"}
        
        # Calculate temporal statistics
        timestamps.sort()
        
        oldest = timestamps[0]
        newest = timestamps[-1]
        time_span = newest - oldest
        
        # Calculate distribution
        distribution = self._calculate_time_distribution(timestamps)
        
        # Detect patterns
        patterns = self._detect_temporal_patterns(timestamps, data_points)
        
        # Determine relevance time window
        relevance_window = self._determine_relevance_window(query, timestamps)
        
        # Calculate temporal score
        temporal_score = self._calculate_temporal_score(timestamps, query)
        
        return {
            "timestamps_analyzed": len(timestamps),
            "oldest_timestamp": oldest.isoformat(),
            "newest_timestamp": newest.isoformat(),
            "time_span_hours": time_span.total_seconds() / 3600,
            "distribution": distribution,
            "patterns_detected": patterns,
            "recommended_time_window": relevance_window,
            "temporal_score": temporal_score,
            "temporal_context": self._generate_temporal_context(timestamps, query),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_timestamp(self, data_point: Dict[str, Any]) -> Optional[datetime]:
        """Extract timestamp from data point"""
        timestamp_fields = [
            "timestamp", "published", "created_at", "date", 
            "time", "last_updated", "processed_at"
        ]
        
        for field in timestamp_fields:
            if field in data_point:
                value = data_point[field]
                if isinstance(value, datetime):
                    return value
                elif isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except:
                        try:
                            # Try common formats
                            formats = [
                                "%Y-%m-%dT%H:%M:%S.%fZ",
                                "%Y-%m-%d %H:%M:%S",
                                "%Y/%m/%d %H:%M:%S",
                                "%a, %d %b %Y %H:%M:%S %Z"
                            ]
                            for fmt in formats:
                                try:
                                    return datetime.strptime(value, fmt)
                                except:
                                    continue
                        except:
                            continue
        
        return None
    
    def _calculate_time_distribution(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Calculate time distribution of data points"""
        if not timestamps:
            return {}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame({
            "timestamp": timestamps,
            "hour": [ts.hour for ts in timestamps],
            "day_of_week": [ts.weekday() for ts in timestamps],
            "date": [ts.date() for ts in timestamps]
        })
        
        # Hourly distribution
        hourly_dist = df["hour"].value_counts().sort_index().to_dict()
        
        # Daily distribution
        daily_dist = df["date"].value_counts().sort_index()
        daily_trend = {
            "dates": [date.isoformat() for date in daily_dist.index],
            "counts": daily_dist.values.tolist()
        }
        
        # Calculate recency
        now = datetime.utcnow()
        recency_stats = {
            "within_1_hour": sum(1 for ts in timestamps if (now - ts).total_seconds() <= 3600),
            "within_6_hours": sum(1 for ts in timestamps if (now - ts).total_seconds() <= 21600),
            "within_24_hours": sum(1 for ts in timestamps if (now - ts).total_seconds() <= 86400),
            "older_than_24_hours": sum(1 for ts in timestamps if (now - ts).total_seconds() > 86400)
        }
        
        return {
            "hourly_distribution": hourly_dist,
            "daily_trend": daily_trend,
            "recency_stats": recency_stats,
            "total_points": len(timestamps)
        }
    
    def _detect_temporal_patterns(self, 
                                 timestamps: List[datetime], 
                                 data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect temporal patterns in data"""
        patterns = []
        
        if len(timestamps) < 3:
            return patterns
        
        # Check for clustering
        time_diffs = np.diff([ts.timestamp() for ts in timestamps])
        avg_diff = np.mean(time_diffs)
        std_diff = np.std(time_diffs)
        
        if std_diff < avg_diff * 0.5:  # Regular intervals
            patterns.append({
                "type": "regular_intervals",
                "avg_interval_seconds": avg_diff,
                "regularity_score": 1 - (std_diff / avg_diff)
            })
        
        # Check for recency bias
        now = datetime.utcnow().timestamp()
        recent_timestamps = [ts for ts in timestamps if (now - ts.timestamp()) <= 3600]
        
        if len(recent_timestamps) > len(timestamps) * 0.5:
            patterns.append({
                "type": "recency_bias",
                "recent_percentage": len(recent_timestamps) / len(timestamps),
                "description": "Most data points are very recent"
            })
        
        # Check for time gaps
        if len(time_diffs) > 0:
            max_gap = max(time_diffs)
            if max_gap > 3600:  # Gap larger than 1 hour
                patterns.append({
                    "type": "time_gap",
                    "gap_seconds": max_gap,
                    "gap_hours": max_gap / 3600,
                    "description": f"Significant time gap of {max_gap/3600:.1f} hours detected"
                })
        
        # Check for seasonal patterns
        hourly_counts = {}
        for ts in timestamps:
            hour = ts.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        peak_hours = [hour for hour, count in hourly_counts.items() 
                     if count > len(timestamps) * 0.1]  # More than 10% of data
        
        if peak_hours:
            patterns.append({
                "type": "peak_hours",
                "hours": sorted(peak_hours),
                "description": f"Peak activity during hours: {sorted(peak_hours)}"
            })
        
        return patterns
    
    def _determine_relevance_window(self, 
                                   query: str, 
                                   timestamps: List[datetime]) -> str:
        """Determine the most relevant time window for a query"""
        query_lower = query.lower()
        
        # Check for explicit time references
        time_keywords = {
            "last hour": "very_recent",
            "last 6 hours": "recent",
            "today": "today",
            "this week": "this_week",
            "this month": "this_month",
            "recent": "recent",
            "latest": "very_recent",
            "historical": "historical",
            "past year": "historical"
        }
        
        for keyword, window in time_keywords.items():
            if keyword in query_lower:
                return window
        
        # Determine based on data recency
        if not timestamps:
            return "recent"  # Default
        
        now = datetime.utcnow()
        newest_age = (now - max(timestamps)).total_seconds() / 3600
        
        if newest_age <= 1:
            return "very_recent"
        elif newest_age <= 6:
            return "recent"
        elif newest_age <= 24:
            return "today"
        elif newest_age <= 168:  # 7 days
            return "this_week"
        else:
            return "historical"
    
    def _calculate_temporal_score(self, 
                                 timestamps: List[datetime], 
                                 query: str) -> float:
        """Calculate temporal relevance score (0-1)"""
        if not timestamps:
            return 0.0
        
        now = datetime.utcnow()
        
        # Calculate average age
        ages = [(now - ts).total_seconds() / 3600 for ts in timestamps]
        avg_age = sum(ages) / len(ages)
        
        # Calculate age diversity
        age_std = np.std(ages) if len(ages) > 1 else 0
        
        # Base score based on recency (lower age = higher score)
        recency_score = 1 / (1 + avg_age/24)  # Decay over 24 hours
        
        # Adjust for diversity (some diversity is good, too much is bad)
        if age_std > 0:
            diversity_score = 1 / (1 + age_std/24)
        else:
            diversity_score = 0.5
        
        # Combine scores
        temporal_score = (recency_score * 0.7) + (diversity_score * 0.3)
        
        # Adjust based on query
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["latest", "recent", "now", "today"]):
            # Recent queries benefit from recency
            temporal_score = min(temporal_score * 1.2, 1.0)
        elif any(word in query_lower for word in ["historical", "trend", "over time"]):
            # Historical queries benefit from diversity
            temporal_score = min(temporal_score * 0.8, 1.0)
        
        return round(temporal_score, 3)
    
    def _generate_temporal_context(self, 
                                  timestamps: List[datetime], 
                                  query: str) -> str:
        """Generate human-readable temporal context"""
        if not timestamps:
            return "No temporal data available"
        
        now = datetime.utcnow()
        oldest = min(timestamps)
        newest = max(timestamps)
        time_span = newest - oldest
        
        # Calculate recency
        newest_age = (now - newest).total_seconds() / 3600
        
        if newest_age <= 1:
            recency = "very recent (within the last hour)"
        elif newest_age <= 6:
            recency = "recent (within the last 6 hours)"
        elif newest_age <= 24:
            recency = "from today"
        elif newest_age <= 168:
            recency = "from this week"
        else:
            recency = "historical"
        
        # Generate context description
        context = f"Data spans {time_span.days} days, from {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}. "
        context += f"The most recent data point is {recency}. "
        
        if len(timestamps) > 10:
            context += f"Analysis based on {len(timestamps)} data points across this time period."
        else:
            context += f"Analysis based on {len(timestamps)} data points."
        
        # Add pattern information
        patterns = self._detect_temporal_patterns(timestamps, [])
        if patterns:
            pattern_descs = []
            for pattern in patterns:
                if pattern["type"] == "peak_hours":
                    pattern_descs.append(f"peak activity during hours {pattern['hours']}")
                elif pattern["type"] == "time_gap":
                    pattern_descs.append(f"significant time gap of {pattern['gap_hours']:.1f} hours")
            
            if pattern_descs:
                context += f" Temporal patterns detected: {', '.join(pattern_descs)}."
        
        return context
    
    def filter_by_time_window(self, 
                             data_points: List[Dict[str, Any]], 
                             time_window: str) -> List[Dict[str, Any]]:
        """Filter data points by time window"""
        if time_window not in self.time_windows:
            logger.warning(f"Unknown time window: {time_window}")
            return data_points
        
        window_delta = self.time_windows[time_window]
        cutoff = datetime.utcnow() - window_delta
        
        filtered_points = []
        for point in data_points:
            timestamp = self._extract_timestamp(point)
            if timestamp and timestamp >= cutoff:
                filtered_points.append(point)
        
        return filtered_points
    
    def enhance_with_temporal_features(self, 
                                      data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance data points with temporal features"""
        enhanced_points = []
        
        for point in data_points:
            enhanced = dict(point)
            timestamp = self._extract_timestamp(point)
            
            if timestamp:
                # Add temporal features
                enhanced["_temporal_features"] = {
                    "hour_of_day": timestamp.hour,
                    "day_of_week": timestamp.weekday(),
                    "day_of_month": timestamp.day,
                    "month": timestamp.month,
                    "is_weekend": timestamp.weekday() >= 5,
                    "is_business_hours": self._is_business_hours(timestamp),
                    "time_since_midnight": timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second,
                    "days_since_epoch": (timestamp - datetime(1970, 1, 1)).days
                }
                
                # Add recency score
                now = datetime.utcnow()
                age_hours = (now - timestamp).total_seconds() / 3600
                enhanced["_temporal_features"]["recency_score"] = 1 / (1 + age_hours/24)
            
            enhanced_points.append(enhanced)
        
        return enhanced_points
    
    def _is_business_hours(self, timestamp: datetime) -> bool:
        """Check if timestamp is during business hours"""
        # 9 AM to 5 PM, Monday to Friday
        if timestamp.weekday() >= 5:  # Saturday or Sunday
            return False
        
        hour = timestamp.hour
        return 9 <= hour < 17
    
    def get_temporal_insights(self, 
                             data_points: List[Dict[str, Any]], 
                             data_type: str = None) -> Dict[str, Any]:
        """Get temporal insights for data points"""
        insights = {
            "timestamp": datetime.utcnow().isoformat(),
            "data_type": data_type,
            "insights": []
        }
        
        if not data_points:
            return insights
        
        # Extract timestamps
        timestamps = []
        for point in data_points:
            ts = self._extract_timestamp(point)
            if ts:
                timestamps.append(ts)
        
        if not timestamps:
            return insights
        
        # Basic insights
        insights["total_points"] = len(data_points)
        insights["points_with_timestamps"] = len(timestamps)
        
        # Time range insight
        oldest = min(timestamps)
        newest = max(timestamps)
        time_span = newest - oldest
        
        insights["insights"].append({
            "type": "time_range",
            "description": f"Data covers {time_span.days} days from {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}",
            "oldest": oldest.isoformat(),
            "newest": newest.isoformat(),
            "span_days": time_span.days
        })
        
        # Recency insight
        now = datetime.utcnow()
        newest_age = (now - newest).total_seconds() / 3600
        
        if newest_age <= 1:
            recency_desc = "Very recent data (last hour)"
        elif newest_age <= 6:
            recency_desc = "Recent data (last 6 hours)"
        elif newest_age <= 24:
            recency_desc = "Today's data"
        else:
            recency_desc = f"Data from {newest_age:.1f} hours ago"
        
        insights["insights"].append({
            "type": "recency",
            "description": recency_desc,
            "hours_since_newest": round(newest_age, 1)
        })
        
        # Distribution insight
        hourly_counts = {}
        for ts in timestamps:
            hour = ts.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        if hourly_counts:
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0]
            insights["insights"].append({
                "type": "peak_activity",
                "description": f"Peak activity at {peak_hour}:00 UTC",
                "peak_hour": peak_hour,
                "peak_count": hourly_counts[peak_hour]
            })
        
        # Data type specific insights
        if data_type == "financial":
            market_hours = [ts for ts in timestamps if 9 <= ts.hour < 17]
            insights["insights"].append({
                "type": "market_hours",
                "description": f"{len(market_hours)} data points during market hours (9AM-5PM)",
                "market_hours_count": len(market_hours),
                "non_market_hours_count": len(timestamps) - len(market_hours)
            })
        
        return insights