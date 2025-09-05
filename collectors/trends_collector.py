import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from sqlalchemy.orm import Session
from models import TrendData
from config import settings

logger = logging.getLogger(__name__)

class TrendsCollector:
    def __init__(self):
        self.queries = settings.trends_queries
        self.countries = settings.trends_countries
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    async def collect_trends_data(self, db: Session) -> List[Dict]:
        """Collect Google Trends data for n8n queries"""
        collected_trends = []
        
        for query in self.queries:
            for country in self.countries:
                try:
                    trend_data = await self._get_trend_data(query, country)
                    if trend_data:
                        # Store in database
                        for date, interest_score in trend_data.items():
                            trend_record = TrendData(
                                query=query,
                                country=country,
                                interest_score=float(interest_score),
                                date=datetime.strptime(date, '%Y-%m-%d')
                            )
                            
                            # Check if record already exists
                            existing_trend = db.query(TrendData).filter(
                                TrendData.query == query,
                                TrendData.country == country,
                                TrendData.date == trend_record.date
                            ).first()
                            
                            if not existing_trend:
                                db.add(trend_record)
                                collected_trends.append({
                                    'query': query,
                                    'country': country,
                                    'interest_score': float(interest_score),
                                    'date': trend_record.date
                                })
                        
                        db.commit()
                        logger.info(f"Collected trends data for '{query}' in {country}")
                        
                except Exception as e:
                    logger.error(f"Error collecting trends for '{query}' in {country}: {e}")
        
        return collected_trends
    
    async def _get_trend_data(self, query: str, country: str) -> Optional[Dict]:
        """Get trend data for a specific query and country"""
        try:
            # Build payload
            self.pytrends.build_payload([query], cat=0, timeframe='today 12-m', geo=country, gprop='')
            
            # Get interest over time
            interest_over_time = self.pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                # Convert to dictionary with date as key and interest score as value
                trend_dict = {}
                for date, row in interest_over_time.iterrows():
                    trend_dict[date.strftime('%Y-%m-%d')] = row[query]
                return trend_dict
            else:
                logger.warning(f"No trend data available for '{query}' in {country}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting trend data for '{query}' in {country}: {e}")
            return None
    
    def get_trending_queries(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get queries with highest average interest scores"""
        from sqlalchemy import func
        
        trending_queries = db.query(
            TrendData.query,
            func.avg(TrendData.interest_score).label('avg_interest'),
            func.max(TrendData.interest_score).label('max_interest'),
            func.count(TrendData.id).label('data_points')
        ).group_by(TrendData.query).order_by(
            func.avg(TrendData.interest_score).desc()
        ).limit(limit).all()
        
        return [
            {
                'query': trend.query,
                'avg_interest': round(trend.avg_interest, 2),
                'max_interest': trend.max_interest,
                'data_points': trend.data_points
            }
            for trend in trending_queries
        ]
    
    def get_country_trends(self, db: Session) -> List[Dict]:
        """Get trend data grouped by country"""
        from sqlalchemy import func
        
        country_trends = db.query(
            TrendData.country,
            func.avg(TrendData.interest_score).label('avg_interest'),
            func.count(TrendData.id).label('data_points')
        ).group_by(TrendData.country).order_by(
            func.avg(TrendData.interest_score).desc()
        ).all()
        
        return [
            {
                'country': trend.country,
                'avg_interest': round(trend.avg_interest, 2),
                'data_points': trend.data_points
            }
            for trend in country_trends
        ]
    
    def get_recent_trends(self, db: Session, days: int = 30) -> List[Dict]:
        """Get recent trend data"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_trends = db.query(TrendData).filter(
            TrendData.date >= cutoff_date
        ).order_by(TrendData.date.desc()).all()
        
        return [
            {
                'query': trend.query,
                'country': trend.country,
                'interest_score': trend.interest_score,
                'date': trend.date
            }
            for trend in recent_trends
        ]
    
    def get_trend_analysis(self, db: Session, query: str) -> Dict:
        """Get detailed trend analysis for a specific query"""
        from sqlalchemy import func
        
        # Get trend data for the query
        trend_data = db.query(TrendData).filter(
            TrendData.query == query
        ).order_by(TrendData.date).all()
        
        if not trend_data:
            return {'error': f'No trend data found for query: {query}'}
        
        # Calculate statistics
        scores = [t.interest_score for t in trend_data]
        countries = list(set([t.country for t in trend_data]))
        
        analysis = {
            'query': query,
            'countries': countries,
            'total_data_points': len(trend_data),
            'avg_interest': round(sum(scores) / len(scores), 2),
            'max_interest': max(scores),
            'min_interest': min(scores),
            'date_range': {
                'start': min([t.date for t in trend_data]).strftime('%Y-%m-%d'),
                'end': max([t.date for t in trend_data]).strftime('%Y-%m-%d')
            },
            'recent_trend': scores[-7:] if len(scores) >= 7 else scores  # Last 7 data points
        }
        
        return analysis
