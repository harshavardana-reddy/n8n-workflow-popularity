import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
from frontend.dashboard import AdvancedDashboard

# Page configuration
st.set_page_config(
    page_title="n8n Workflow Popularity Tracker - Advanced",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

class APIClient:
    """Enhanced API client with caching"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache is still valid"""
        if key not in self.cache:
            return False
        return time.time() - self.cache[key]['timestamp'] < self.cache_timeout
    
    def _get_cached_data(self, key: str):
        """Get data from cache"""
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None
    
    def _set_cache(self, key: str, data):
        """Set data in cache"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_workflows(self, use_cache: bool = True) -> List[Dict]:
        """Get all workflows with caching"""
        cache_key = "workflows"
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            response = requests.get(f"{self.base_url}/workflows")
            response.raise_for_status()
            data = response.json()
            
            if use_cache:
                self._set_cache(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching workflows: {e}")
            return []
    
    def get_workflows_by_platform(self, platform: str, use_cache: bool = True) -> List[Dict]:
        """Get workflows by platform with caching"""
        cache_key = f"workflows_{platform}"
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            response = requests.get(f"{self.base_url}/workflows/{platform}")
            response.raise_for_status()
            data = response.json()
            
            if use_cache:
                self._set_cache(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching {platform} workflows: {e}")
            return []
    
    def get_top_workflows(self, n: int, use_cache: bool = True) -> List[Dict]:
        """Get top N workflows with caching"""
        cache_key = f"top_workflows_{n}"
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            response = requests.get(f"{self.base_url}/workflows/top/{n}")
            response.raise_for_status()
            data = response.json()
            
            if use_cache:
                self._set_cache(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching top {n} workflows: {e}")
            return []
    
    def get_workflow_stats(self, use_cache: bool = True) -> Dict:
        """Get workflow statistics with caching"""
        cache_key = "workflow_stats"
        
        if use_cache:
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            response = requests.get(f"{self.base_url}/workflows/stats")
            response.raise_for_status()
            data = response.json()
            
            if use_cache:
                self._set_cache(cache_key, data)
            
            return data
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching workflow stats: {e}")
            return {}
    
    def collect_data(self, platform: str = "all") -> bool:
        """Trigger data collection"""
        try:
            if platform == "all":
                response = requests.post(f"{self.base_url}/collect/all")
            else:
                response = requests.post(f"{self.base_url}/collect/{platform}")
            response.raise_for_status()
            
            # Clear cache after data collection
            self.cache.clear()
            
            return True
        except requests.exceptions.RequestException as e:
            st.error(f"Error collecting {platform} data: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

def render_sidebar(api_client: APIClient):
    """Render sidebar with controls"""
    with st.sidebar:
        st.header("📊 Dashboard Controls")
        
        # API Status
        if api_client.health_check():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.info("Make sure the FastAPI server is running on http://localhost:8000")
            return False
        
        # Platform filter
        platform = st.selectbox(
            "Select Platform",
            ["All", "YouTube", "Forum", "Google"],
            help="Filter workflows by platform"
        )
        
        # Number of top workflows
        top_n = st.slider(
            "Top N Workflows",
            min_value=5,
            max_value=50,
            value=10,
            help="Number of top workflows to display"
        )
        
        # Auto-refresh
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
        
        # Cache control
        use_cache = st.checkbox("Use Cache", value=True, help="Enable caching for better performance")
        
        # Data collection buttons
        st.header("🔄 Data Collection")
        if st.button("🔄 Refresh All Data"):
            with st.spinner("Collecting data from all platforms..."):
                if api_client.collect_data("all"):
                    st.success("Data collection started!")
                    time.sleep(2)
                    st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📺 YouTube"):
                with st.spinner("Collecting YouTube data..."):
                    if api_client.collect_data("youtube"):
                        st.success("YouTube data collection started!")
                        time.sleep(2)
                        st.rerun()
        
        with col2:
            if st.button("💬 Forum"):
                with st.spinner("Collecting Forum data..."):
                    if api_client.collect_data("forum"):
                        st.success("Forum data collection started!")
                        time.sleep(2)
                        st.rerun()
        
        # Clear cache button
        if st.button("🗑️ Clear Cache"):
            api_client.cache.clear()
            st.success("Cache cleared!")
            st.rerun()
        
        return platform, top_n, auto_refresh, use_cache

def render_main_dashboard(api_client: APIClient, platform: str, top_n: int, use_cache: bool):
    """Render main dashboard content"""
    
    # Get data
    if platform == "All":
        workflows = api_client.get_workflows(use_cache)
        title = "All Workflows"
    else:
        workflows = api_client.get_workflows_by_platform(platform, use_cache)
        title = f"{platform} Workflows"
    
    if not workflows:
        st.warning("No workflows found. Try collecting data first!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(workflows)
    
    # Statistics cards
    st.header("📈 Statistics")
    stats = api_client.get_workflow_stats(use_cache)
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Workflows",
                value=stats.get("total_workflows", 0)
            )
        
        with col2:
            st.metric(
                label="YouTube Videos",
                value=stats.get("youtube_workflows", 0)
            )
        
        with col3:
            st.metric(
                label="Forum Posts",
                value=stats.get("forum_workflows", 0)
            )
        
        with col4:
            st.metric(
                label="Trends Data",
                value=stats.get("trends_workflows", 0)
            )
    
    # Top workflows section
    st.header(f"🏆 Top {top_n} Workflows")
    top_workflows = api_client.get_top_workflows(top_n, use_cache)
    
    if top_workflows:
        top_df = pd.DataFrame(top_workflows)
        
        # Create engagement score for ranking
        top_df['engagement_score'] = (
            top_df['popularity_metrics'].apply(lambda x: x['views']) * 0.4 +
            top_df['popularity_metrics'].apply(lambda x: x['likes']) * 0.3 +
            top_df['popularity_metrics'].apply(lambda x: x['comments']) * 0.2 +
            (top_df['popularity_metrics'].apply(lambda x: x['like_to_view_ratio']) + 
             top_df['popularity_metrics'].apply(lambda x: x['comment_to_view_ratio'])) * 1000 * 0.1
        )
        
        # Display top workflows
        for i, workflow in enumerate(top_workflows[:top_n], 1):
            with st.expander(f"#{i} {workflow['workflow']} ({workflow['platform']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Views", f"{workflow['popularity_metrics']['views']:,}")
                    st.metric("Likes", f"{workflow['popularity_metrics']['likes']:,}")
                
                with col2:
                    st.metric("Comments", f"{workflow['popularity_metrics']['comments']:,}")
                    st.metric("Like Ratio", f"{workflow['popularity_metrics']['like_to_view_ratio']:.3f}")
                
                with col3:
                    st.metric("Comment Ratio", f"{workflow['popularity_metrics']['comment_to_view_ratio']:.3f}")
                    st.metric("Country", workflow['country'])
                
                st.caption(f"Last updated: {workflow['last_updated']}")
    
    # Platform distribution
    st.header("📊 Platform Distribution")
    
    if len(workflows) > 0:
        platform_counts = df['platform'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                values=platform_counts.values,
                names=platform_counts.index,
                title="Workflows by Platform"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart
            fig_bar = px.bar(
                x=platform_counts.index,
                y=platform_counts.values,
                title="Workflows by Platform",
                labels={'x': 'Platform', 'y': 'Count'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Engagement metrics
    st.header("📈 Engagement Metrics")
    
    if len(workflows) > 0:
        # Extract metrics for visualization
        df['views'] = df['popularity_metrics'].apply(lambda x: x['views'])
        df['likes'] = df['popularity_metrics'].apply(lambda x: x['likes'])
        df['comments'] = df['popularity_metrics'].apply(lambda x: x['comments'])
        df['like_ratio'] = df['popularity_metrics'].apply(lambda x: x['like_to_view_ratio'])
        df['comment_ratio'] = df['popularity_metrics'].apply(lambda x: x['comment_to_view_ratio'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Views vs Likes scatter plot
            fig_scatter = px.scatter(
                df,
                x='views',
                y='likes',
                color='platform',
                title="Views vs Likes",
                hover_data=['workflow']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Engagement ratios by platform
            fig_box = px.box(
                df,
                x='platform',
                y='like_ratio',
                title="Like-to-View Ratio by Platform"
            )
            st.plotly_chart(fig_box, use_container_width=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🚀 n8n Workflow Popularity Tracker - Advanced")
    st.markdown("Track the most popular n8n workflows across YouTube, Forum, and Google Trends")
    
    # Initialize API client
    api_client = APIClient()
    
    # Render sidebar
    sidebar_result = render_sidebar(api_client)
    if sidebar_result is False:
        return
    
    platform, top_n, auto_refresh, use_cache = sidebar_result
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Main Dashboard", "📈 Trends Analysis", "💡 Insights", "📤 Export"])
    
    with tab1:
        render_main_dashboard(api_client, platform, top_n, use_cache)
    
    with tab2:
        # Initialize advanced dashboard
        advanced_dashboard = AdvancedDashboard()
        
        # Get workflows for analysis
        if platform == "All":
            workflows = api_client.get_workflows(use_cache)
        else:
            workflows = api_client.get_workflows_by_platform(platform, use_cache)
        
        advanced_dashboard.render_trends_analysis()
        advanced_dashboard.render_forum_analysis()
        advanced_dashboard.render_workflow_comparison(workflows)
    
    with tab3:
        # Get workflows for insights
        if platform == "All":
            workflows = api_client.get_workflows(use_cache)
        else:
            workflows = api_client.get_workflows_by_platform(platform, use_cache)
        
        advanced_dashboard = AdvancedDashboard()
        advanced_dashboard.render_workflow_insights(workflows)
    
    with tab4:
        # Get workflows for export
        if platform == "All":
            workflows = api_client.get_workflows(use_cache)
        else:
            workflows = api_client.get_workflows_by_platform(platform, use_cache)
        
        advanced_dashboard = AdvancedDashboard()
        advanced_dashboard.render_export_options(workflows)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using Streamlit | "
        "API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)"
    )

if __name__ == "__main__":
    main()
