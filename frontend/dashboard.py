import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional

class AdvancedDashboard:
    """Advanced dashboard with additional features"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
    
    def get_workflow_trends(self) -> Dict:
        """Get trending workflows over time"""
        try:
            response = requests.get(f"{self.api_base_url}/trends/recent?days=30")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching trends: {e}")
            return []
    
    def get_country_trends(self) -> Dict:
        """Get trends by country"""
        try:
            response = requests.get(f"{self.api_base_url}/trends/countries")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching country trends: {e}")
            return []
    
    def get_forum_categories(self) -> Dict:
        """Get forum categories"""
        try:
            response = requests.get(f"{self.api_base_url}/forum/categories")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching forum categories: {e}")
            return []
    
    def render_trends_analysis(self):
        """Render trends analysis section"""
        st.header("📈 Trends Analysis")
        
        # Get trends data
        trends_data = self.get_workflow_trends()
        country_trends = self.get_country_trends()
        
        if trends_data:
            trends_df = pd.DataFrame(trends_data)
            trends_df['date'] = pd.to_datetime(trends_df['date'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Interest over time
                fig_trends = px.line(
                    trends_df,
                    x='date',
                    y='interest_score',
                    color='query',
                    title="Interest Score Over Time"
                )
                st.plotly_chart(fig_trends, use_container_width=True)
            
            with col2:
                # Country trends
                if country_trends:
                    country_df = pd.DataFrame(country_trends)
                    fig_country = px.bar(
                        country_df,
                        x='country',
                        y='avg_interest',
                        title="Average Interest by Country"
                    )
                    st.plotly_chart(fig_country, use_container_width=True)
    
    def render_forum_analysis(self):
        """Render forum analysis section"""
        st.header("💬 Forum Analysis")
        
        categories = self.get_forum_categories()
        
        if categories:
            categories_df = pd.DataFrame(categories)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Categories pie chart
                fig_categories = px.pie(
                    categories_df,
                    values='post_count',
                    names='category',
                    title="Posts by Category"
                )
                st.plotly_chart(fig_categories, use_container_width=True)
            
            with col2:
                # Engagement by category
                fig_engagement = px.bar(
                    categories_df,
                    x='category',
                    y='total_views',
                    title="Total Views by Category"
                )
                st.plotly_chart(fig_engagement, use_container_width=True)
    
    def render_workflow_comparison(self, workflows: List[Dict]):
        """Render workflow comparison section"""
        st.header("⚖️ Workflow Comparison")
        
        if not workflows:
            st.warning("No workflows available for comparison")
            return
        
        df = pd.DataFrame(workflows)
        df['views'] = df['popularity_metrics'].apply(lambda x: x['views'])
        df['likes'] = df['popularity_metrics'].apply(lambda x: x['likes'])
        df['comments'] = df['popularity_metrics'].apply(lambda x: x['comments'])
        df['like_ratio'] = df['popularity_metrics'].apply(lambda x: x['like_to_view_ratio'])
        df['comment_ratio'] = df['popularity_metrics'].apply(lambda x: x['comment_to_view_ratio'])
        
        # Platform comparison
        platform_stats = df.groupby('platform').agg({
            'views': ['mean', 'sum'],
            'likes': ['mean', 'sum'],
            'comments': ['mean', 'sum'],
            'like_ratio': 'mean',
            'comment_ratio': 'mean'
        }).round(3)
        
        st.subheader("Platform Performance Comparison")
        st.dataframe(platform_stats, use_container_width=True)
        
        # Correlation matrix
        st.subheader("Metrics Correlation")
        correlation_data = df[['views', 'likes', 'comments', 'like_ratio', 'comment_ratio']].corr()
        
        fig_corr = px.imshow(
            correlation_data,
            text_auto=True,
            aspect="auto",
            title="Metrics Correlation Matrix"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    def render_workflow_insights(self, workflows: List[Dict]):
        """Render workflow insights section"""
        st.header("💡 Workflow Insights")
        
        if not workflows:
            st.warning("No workflows available for insights")
            return
        
        df = pd.DataFrame(workflows)
        df['views'] = df['popularity_metrics'].apply(lambda x: x['views'])
        df['likes'] = df['popularity_metrics'].apply(lambda x: x['likes'])
        df['comments'] = df['popularity_metrics'].apply(lambda x: x['comments'])
        df['like_ratio'] = df['popularity_metrics'].apply(lambda x: x['like_to_view_ratio'])
        df['comment_ratio'] = df['popularity_metrics'].apply(lambda x: x['comment_to_view_ratio'])
        
        # Calculate insights
        total_workflows = len(df)
        avg_views = df['views'].mean()
        avg_likes = df['likes'].mean()
        avg_comments = df['comments'].mean()
        avg_like_ratio = df['like_ratio'].mean()
        avg_comment_ratio = df['comment_ratio'].mean()
        
        # Top performers
        top_viewed = df.loc[df['views'].idxmax()]
        top_liked = df.loc[df['likes'].idxmax()]
        top_engaged = df.loc[df['like_ratio'].idxmax()]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Workflows", f"{total_workflows:,}")
            st.metric("Avg Views", f"{avg_views:,.0f}")
            st.metric("Avg Likes", f"{avg_likes:,.0f}")
        
        with col2:
            st.metric("Avg Comments", f"{avg_comments:,.0f}")
            st.metric("Avg Like Ratio", f"{avg_like_ratio:.3f}")
            st.metric("Avg Comment Ratio", f"{avg_comment_ratio:.3f}")
        
        with col3:
            st.metric("Top Viewed", f"{top_viewed['views']:,}")
            st.metric("Top Liked", f"{top_liked['likes']:,}")
            st.metric("Top Engaged", f"{top_engaged['like_ratio']:.3f}")
        
        # Insights text
        st.subheader("Key Insights")
        
        insights = []
        
        if avg_like_ratio > 0.05:
            insights.append("✅ High engagement: Average like ratio is above 5%")
        else:
            insights.append("⚠️ Low engagement: Average like ratio is below 5%")
        
        if avg_comment_ratio > 0.01:
            insights.append("✅ Active community: High comment ratio indicates active discussion")
        else:
            insights.append("⚠️ Low interaction: Comment ratio could be improved")
        
        platform_distribution = df['platform'].value_counts()
        dominant_platform = platform_distribution.index[0]
        insights.append(f"📊 {dominant_platform} is the dominant platform with {platform_distribution.iloc[0]} workflows")
        
        for insight in insights:
            st.write(insight)
    
    def render_export_options(self, workflows: List[Dict]):
        """Render export options"""
        st.header("📤 Export Options")
        
        if not workflows:
            st.warning("No workflows available for export")
            return
        
        df = pd.DataFrame(workflows)
        
        # Flatten the popularity_metrics column
        df['views'] = df['popularity_metrics'].apply(lambda x: x['views'])
        df['likes'] = df['popularity_metrics'].apply(lambda x: x['likes'])
        df['comments'] = df['popularity_metrics'].apply(lambda x: x['comments'])
        df['like_ratio'] = df['popularity_metrics'].apply(lambda x: x['like_to_view_ratio'])
        df['comment_ratio'] = df['popularity_metrics'].apply(lambda x: x['comment_to_view_ratio'])
        
        # Remove the nested column
        df = df.drop('popularity_metrics', axis=1)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV Export
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"n8n_workflows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON Export
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"n8n_workflows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col3:
            # Excel Export
            excel_buffer = pd.ExcelWriter("temp_workflows.xlsx", engine='openpyxl')
            df.to_excel(excel_buffer, index=False, sheet_name='Workflows')
            excel_buffer.close()
            
            with open("temp_workflows.xlsx", "rb") as f:
                excel_data = f.read()
            
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"n8n_workflows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
