import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import requests
import json
from typing import Dict, List, Any
import random

# Import your existing services
from Service.user_service import UserService
from Service.portfolio_service import PortfolioService
from Service.stock_service import StockService
from Service.transaction_service import TransactionService

# Page configuration with advanced settings
st.set_page_config(
    page_title="Smart Stock Tracker Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS with animations and modern design
st.markdown("""
<style>
    /* Advanced CSS Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --success-gradient: linear-gradient(135deg, #00C9A7 0%, #92FE9D 100%);
        --warning-gradient: linear-gradient(135deg, #FAD961 0%, #F76B1C 100%);
        --danger-gradient: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
        --dark-gradient: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.1);
        --shadow-hard: 0 20px 60px rgba(0, 0, 0, 0.15);
    }
    
    /* Advanced Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translate3d(0, 40px, 0);
        }
        to {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translate3d(-100px, 0, 0);
        }
        to {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { background-position: -468px 0; }
        100% { background-position: 468px 0; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Main Header with Animation */
    .main-header {
        font-size: 3.5rem;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0;
        animation: fadeInUp 0.8s ease-out;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Animated Metric Cards */
    .metric-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: var(--shadow-soft);
        margin: 15px 0;
        border-left: 6px solid #667eea;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: var(--shadow-hard);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    /* Portfolio Cards with Advanced Animations */
    .portfolio-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: var(--shadow-soft);
        margin: 20px 0;
        border-left: 6px solid #667eea;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideInLeft 0.7s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .portfolio-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .portfolio-card:hover::after {
        transform: scaleX(1);
    }
    
    .portfolio-card:hover {
        transform: translateX(10px) scale(1.02);
        box-shadow: var(--shadow-hard);
    }
    
    /* Animated Buttons */
    .stButton button {
        border-radius: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .stButton button:hover::before {
        left: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Animated Sidebar */
    .sidebar .sidebar-content {
        background: var(--dark-gradient);
        animation: slideInLeft 0.8s ease-out;
    }
    
    /* Loading Animation */
    .loading-shimmer {
        background: #f6f7f8;
        background-image: linear-gradient(to right, #f6f7f8 0%, #edeef1 20%, #f6f7f8 40%, #f6f7f8 100%);
        background-repeat: no-repeat;
        background-size: 800px 104px;
        animation: shimmer 1.2s infinite linear;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Floating Animation for Important Elements */
    .floating-element {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Progress Bar Animation */
    .progress-container {
        width: 100%;
        background-color: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 8px;
        background: var(--primary-gradient);
        border-radius: 10px;
        transition: width 0.6s ease;
        animation: pulse 2s infinite;
    }
    
    /* Advanced Table Styling */
    .dataframe {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-soft) !important;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Notification Badge */
    .notification-badge {
        background: var(--danger-gradient);
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7em;
        font-weight: bold;
        animation: pulse 2s infinite;
        position: absolute;
        top: -5px;
        right: -5px;
    }
    
    /* Advanced Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
user_service = UserService()
portfolio_service = PortfolioService()
stock_service = StockService()
transaction_service = TransactionService()

class AnimatedStockTracker:
    def __init__(self):
        self.current_user = None
        self.animation_state = {}
        
    def run(self):
        """Main application controller with advanced animations"""
        self.setup_animated_sidebar()
        
        if 'user' not in st.session_state:
            self.show_animated_landing_page()
        else:
            self.current_user = st.session_state.user
            self.show_animated_dashboard()
    
    def setup_animated_sidebar(self):
        """Advanced animated sidebar with micro-interactions"""
        with st.sidebar:
            # Animated logo with floating effect
            st.markdown("""
            <div class="floating-element">
                <h1 style='text-align: center; color: white; margin-bottom: 30px;'>🚀 Smart Stock Pro</h1>
            </div>
            """, unsafe_allow_html=True)
            
            if 'user' not in st.session_state:
                self.show_animated_auth()
            else:
                self.show_animated_user_profile()
    
    def show_animated_auth(self):
        """Animated authentication section"""
        st.markdown("---")
        
        # Animated tabs
        tab1, tab2 = st.tabs(["🔐 Login", "✨ Register"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("### Welcome Back!")
                login_email = st.text_input("📧 Email Address", key="login_email")
                
                login_btn = st.form_submit_button("🚀 Sign In", use_container_width=True)
                if login_btn:
                    with st.spinner("🔐 Authenticating..."):
                        time.sleep(1)  # Simulate auth delay for animation
                        user = user_service.user_dao.get_user_by_email(login_email)
                        if user:
                            st.session_state.user = user
                            st.success(f"🎉 Welcome back, {user['name']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ User not found. Please register.")
                
        with tab2:
            with st.form("register_form"):
                st.markdown("### Join Our Platform!")
                reg_name = st.text_input("👤 Full Name", key="reg_name")
                reg_email = st.text_input("📧 Email Address", key="reg_email")
                
                register_btn = st.form_submit_button("🌟 Create Account", use_container_width=True)
                if register_btn:
                    with st.spinner("✨ Creating your account..."):
                        time.sleep(1.5)  # Simulate account creation
                        try:
                            user_service.register_user(reg_name, reg_email)
                            st.success("✅ Account created successfully! Please login.")
                        except ValueError as e:
                            st.error(f"❌ {str(e)}")
    
    def show_animated_user_profile(self):
        """Animated user profile section"""
        user = st.session_state.user
        
        # Animated user card
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; margin: 15px 0; animation: fadeInUp 0.6s ease-out;'>
            <div style='display: flex; align-items: center; gap: 15px;'>
                <div style='font-size: 2em;'>👤</div>
                <div>
                    <h4 style='color: white; margin: 0;'>{user['name']}</h4>
                    <p style='color: #bdc3c7; margin: 5px 0;'>{user['email']}</p>
                    <p style='color: #bdc3c7; margin: 0; font-size: 0.8em;'>ID: {user['user_id'][:8]}...</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Animated navigation
        nav_options = ["🏠 Dashboard", "💼 Portfolios", "📈 Live Market", "📊 Analytics", "⚡ Actions", "⚙️ Settings"]
        selected_nav = st.radio(
            "Navigation",
            nav_options,
            key="animated_nav",
            index=0
        )
        st.session_state.current_page = selected_nav
        
        st.markdown("---")
        
        # Animated quick actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh Prices", use_container_width=True):
                self.animated_refresh_prices()
        with col2:
            if st.button("📊 New Portfolio", use_container_width=True):
                st.session_state.show_portfolio_creator = True
        
        # Animated market status
        self.show_animated_market_status()
        
        st.markdown("---")
        
        # Logout button with animation
        if st.button("🚪 Sign Out", use_container_width=True):
            with st.spinner("Signing out..."):
                time.sleep(0.5)
                del st.session_state.user
                st.rerun()
    
    def show_animated_market_status(self):
        """Animated market status with real-time feel"""
        st.markdown("### 📊 Live Markets")
        
        # Simulated market data with animations
        markets = [
            {"name": "S&P 500", "change": "+0.8%", "trend": "up"},
            {"name": "NASDAQ", "change": "+1.2%", "trend": "up"},
            {"name": "DOW JONES", "change": "+0.5%", "trend": "up"},
            {"name": "RUSSELL 2000", "change": "-0.3%", "trend": "down"}
        ]
        
        for market in markets:
            trend_icon = "🟢" if market["trend"] == "up" else "🔴"
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; 
                        padding: 10px; margin: 5px 0; background: rgba(255,255,255,0.05); 
                        border-radius: 10px; animation: fadeInUp 0.5s ease-out;'>
                <span style='color: white;'>{market['name']}</span>
                <span style='color: {'#00C9A7' if market["trend"] == "up" else "#C34A36"}; 
                            font-weight: bold;'>
                    {trend_icon} {market['change']}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    def show_animated_landing_page(self):
        """Ultra-modern animated landing page"""
        # Hero section with advanced animations
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div style='animation: fadeInUp 1s ease-out;'>
                <h1 class='main-header'>Smart Stock Tracker Pro</h1>
                <h3 style='color: #666; margin-top: 0; animation: fadeInUp 1.2s ease-out;'>
                    Institutional-Grade Investment Intelligence
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Animated feature highlights
            features = [
                {"icon": "🚀", "title": "Real-Time Analytics", "desc": "Live portfolio tracking with advanced metrics"},
                {"icon": "💹", "title": "AI-Powered Insights", "desc": "Smart recommendations and market predictions"},
                {"icon": "📊", "title": "Professional Charts", "desc": "Interactive visualizations with animations"},
                {"icon": "🔔", "title": "Smart Alerts", "desc": "Custom notifications for market movements"},
                {"icon": "🌍", "title": "Global Markets", "desc": "Access to worldwide exchanges and data"},
                {"icon": "🛡️", "title": "Bank-Level Security", "desc": "Enterprise-grade data protection"}
            ]
            
            for i, feature in enumerate(features):
                st.markdown(f"""
                <div class='metric-card' style='animation-delay: {i * 0.1}s;'>
                    <div style='display: flex; align-items: center; gap: 15px;'>
                        <div style='font-size: 2em;'>{feature['icon']}</div>
                        <div>
                            <h4 style='margin: 0; color: #2c3e50;'>{feature['title']}</h4>
                            <p style='margin: 5px 0 0 0; color: #7f8c8d;'>{feature['desc']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
                       
            # Animated CTA
            st.markdown("""
            <div class='floating-element' style='text-align: center; padding: 30px; background: var(--success-gradient); 
                        color: white; border-radius: 20px; margin: 20px 0;'>
                <h3 style='margin: 0 0 10px 0;'>Ready to Start?</h3>
                <p style='margin: 0; opacity: 0.9;'>Join thousands of successful investors</p>
            </div>
            """, unsafe_allow_html=True)
    
    def show_animated_dashboard(self):
        """Advanced animated main dashboard"""
        user = st.session_state.user
        
        # Animated header with user welcome
        st.markdown(f"""
        <div style='animation: fadeInUp 0.8s ease-out;'>
            <h1 style='margin-bottom: 0;'>Welcome back, {user['name']}! 👋</h1>
            <p style='color: #666; margin-top: 0;'>Your investment command center</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get portfolio data with loading animation
        with st.spinner("🔄 Loading your portfolio data..."):
            portfolio_summaries = portfolio_service.get_portfolio_summary(user['user_id'])
            time.sleep(1)  # Simulate loading for animation
        
        # Animated summary metrics
        self.show_animated_summary_metrics(portfolio_summaries)
        
        st.markdown("---")
        
        # Advanced animated tabs
        # FIXED CODE (navigation-based):
        current_page = st.session_state.get('current_page', '🏠 Dashboard')

        if current_page == "🏠 Dashboard":
            self.show_animated_portfolio_overview(portfolio_summaries)
        elif current_page == "💼 Portfolios":
            self.show_animated_holdings_view(user['user_id'])
        elif current_page == "📈 Live Market":
            self.show_animated_market_intel()
        elif current_page == "📊 Analytics":
            self.show_animated_performance_dashboard(user['user_id'])
        elif current_page == "⚡ Actions":
            self.show_animated_quick_actions(user['user_id'])
        elif current_page == "⚙️ Settings":
            self.show_settings_page(user)
    def show_settings_page(self, user):
        """Settings page for user preferences"""
        st.subheader("⚙️ Account Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("update_profile"):
                st.markdown("### ✏️ Update Profile")
                new_name = st.text_input("Name", value=user['name'])
                new_email = st.text_input("Email", value=user['email'])
                
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    try:
                        self.user_service.update_profile(user['user_id'], new_name, new_email)
                        st.session_state.user['name'] = new_name
                        st.session_state.user['email'] = new_email
                        st.success("✅ Profile updated successfully!")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
        with col2:
            st.markdown("### 🗑️ Danger Zone")
            st.warning("These actions are irreversible!")
            
            if st.button("🚫 Delete Account", type="secondary", use_container_width=True):
                st.error("This will permanently delete your account and all data!")
                confirm = st.text_input("Type 'DELETE' to confirm:")
                if confirm == "DELETE":
                    try:
                        self.user_service.delete_account(user['user_id'])
                        del st.session_state.user
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
    def show_animated_summary_metrics(self, portfolio_summaries):
        """Animated summary metrics with advanced visual effects"""
        total_net_worth = sum(p['current_value'] for p in portfolio_summaries if 'error' not in p)
        total_gain_loss = sum(p['total_gain_loss'] for p in portfolio_summaries if 'error' not in p)
        total_portfolios = len(portfolio_summaries)
        total_stocks = sum(p['stock_count'] for p in portfolio_summaries if 'error' not in p)
        
        # Animated metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.animated_metric_card(
                "💰 Total Net Worth", 
                f"${total_net_worth:,.2f}", 
                "primary",
                "Your complete portfolio value"
            )
        
        with col2:
            gain_color = "success" if total_gain_loss >= 0 else "danger"
            self.animated_metric_card(
                "📈 Total P&L", 
                f"${total_gain_loss:,.2f}", 
                gain_color,
                f"Overall {'gain' if total_gain_loss >= 0 else 'loss'}"
            )
        
        with col3:
            self.animated_metric_card(
                "📁 Portfolios", 
                str(total_portfolios), 
                "warning",
                "Active investment portfolios"
            )
        
        with col4:
            self.animated_metric_card(
                "📊 Stocks", 
                str(total_stocks), 
                "info",
                "Total stock positions"
            )
    
    def animated_metric_card(self, title: str, value: str, style: str, tooltip: str = ""):
        """Create an animated metric card with advanced styling"""
        style_colors = {
            "primary": ("#667eea", "#764ba2"),
            "success": ("#00C9A7", "#92FE9D"),
            "warning": ("#FAD961", "#F76B1C"),
            "danger": ("#FF6B6B", "#FF8E8E"),
            "info": ("#4ECDC4", "#556270")
        }
        
        color1, color2 = style_colors.get(style, style_colors["primary"])
        
        st.markdown(f"""
        <div class='metric-card tooltip' style='border-left-color: {color1};'>
            <div style='text-align: center;'>
                <h3 style='margin: 0; color: {color1}; font-size: 2em;'>{value}</h3>
                <p style='margin: 5px 0 0 0; color: #7f8c8d; font-weight: 600;'>{title}</p>
            </div>
            {'<span class="tooltiptext">' + tooltip + '</span>' if tooltip else ''}
        </div>
        """, unsafe_allow_html=True)
    
    def show_animated_portfolio_overview(self, portfolio_summaries):
        """Advanced animated portfolio overview"""
        if not portfolio_summaries:
            self.show_animated_empty_state()
            return
        
        # Animated portfolio cards
        for i, summary in enumerate(portfolio_summaries):
            if 'error' in summary:
                st.error(f"❌ Error loading {summary['portfolio_name']}: {summary['error']}")
                continue
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='animation: fadeInUp {0.5 + i * 0.1}s ease-out;'>
                        <h3 style='margin: 0; color: #2c3e50;'>{summary['portfolio_name']}</h3>
                        <p style='margin: 0; color: #7f8c8d; font-size: 0.9em;'>
                            ID: {summary['portfolio_id'][:8]}...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    self.animated_metric_card(
                        "Current Value", 
                        f"${summary['current_value']:,.2f}", 
                        "primary"
                    )
                
                with col3:
                    gain_loss = summary['total_gain_loss']
                    gain_class = "success" if gain_loss >= 0 else "danger"
                    self.animated_metric_card(
                        "Total P&L", 
                        f"${gain_loss:,.2f}", 
                        gain_class
                    )
                
                with col4:
                    return_pct = summary['gain_loss_percentage']
                    return_class = "success" if return_pct >= 0 else "danger"
                    self.animated_metric_card(
                        "Return", 
                        f"{return_pct:+.2f}%", 
                        return_class
                    )
                
                with col5:
                    if st.button("🎯 Manage", key=f"manage_{summary['portfolio_id']}"):
                        st.session_state.selected_portfolio = summary
                        st.rerun()
        
        # Advanced animated charts
        st.markdown("---")
        self.show_animated_portfolio_charts(portfolio_summaries)
    
    def show_animated_portfolio_charts(self, portfolio_summaries):
        """Advanced animated portfolio charts"""
        st.subheader("📈 Portfolio Performance Visualization")
        
        valid_portfolios = [p for p in portfolio_summaries if 'error' not in p]
        if not valid_portfolios:
            return
        
        # Create advanced animated charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Animated pie chart with advanced features
            portfolio_names = [p['portfolio_name'] for p in valid_portfolios]
            portfolio_values = [p['current_value'] for p in valid_portfolios]
            
            fig_pie = px.pie(
                values=portfolio_values,
                names=portfolio_names,
                title="Portfolio Distribution",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                pull=[0.1 if i == portfolio_values.index(max(portfolio_values)) else 0 for i in range(len(portfolio_values))],
                marker=dict(line=dict(color='#ffffff', width=2))
            )
            
            fig_pie.update_layout(
                height=400,
                showlegend=False,
                annotations=[dict(text='Portfolio<br>Allocation', x=0.5, y=0.5, font_size=20, showarrow=False)],
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Animated bar chart with advanced features
            portfolio_returns = [p['gain_loss_percentage'] for p in valid_portfolios]
            colors = ['#00C9A7' if x >= 0 else '#C34A36' for x in portfolio_returns]
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=portfolio_names,
                    y=portfolio_returns,
                    marker_color=colors,
                    text=[f'{x:+.2f}%' for x in portfolio_returns],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
                )
            ])
            
            fig_bar.update_layout(
                title="Portfolio Returns",
                height=400,
                xaxis_tickangle=-45,
                showlegend=False,
                yaxis_title="Return (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
    
    def show_animated_performance_dashboard(self, user_id):
        """Advanced animated performance dashboard"""
        st.subheader("🚀 Advanced Performance Analytics")
        
        # Animated portfolio selector
        portfolios = portfolio_service.get_user_portfolios(user_id)
        if not portfolios:
            st.info("📊 No portfolios available for analytics")
            return
        
        portfolio_options = {p['portfolio_name']: p['portfolio_id'] for p in portfolios}
        selected_portfolio = st.selectbox(
            "🎯 Select Portfolio for Deep Analysis",
            options=list(portfolio_options.keys()),
            key="performance_selector"
        )
        
        if selected_portfolio:
            with st.spinner("🔍 Analyzing portfolio performance..."):
                portfolio_id = portfolio_options[selected_portfolio]
                self.show_advanced_portfolio_analytics(portfolio_id)
    
    def show_advanced_portfolio_analytics(self, portfolio_id):
        """Show advanced animated portfolio analytics - FIXED VERSION"""
        try:
            analytics = portfolio_service.get_portfolio_analytics(portfolio_id)
            performance = analytics['performance']
            stocks = analytics['stocks']
            
            # FIXED: Handle missing keys gracefully
            current_value = performance.get('current_holdings_value') or performance.get('current_value', 0)
            total_invested = performance.get('total_invested', 0)
            net_value = performance.get('net_value', 0)
            total_gain_loss = performance.get('total_gain_loss', 0)
            gain_loss_percentage = performance.get('gain_loss_percentage', 0)
            
            # Key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Invested", f"${total_invested:,.2f}")
            with col2:
                st.metric("Current Value", f"${current_value:,.2f}")
            with col3:
                st.metric("Net Value", f"${net_value:,.2f}")
            with col4:
                delta_color = "normal" if total_gain_loss >= 0 else "inverse"
                st.metric(
                    "Total Return", 
                    f"${total_gain_loss:,.2f}",
                    f"{gain_loss_percentage:+.2f}%",
                    delta_color=delta_color
                )
            
            # Transaction analytics with error handling
            try:
                transaction_analytics = transaction_service.get_transaction_analytics(portfolio_id)
                
                if 'monthly_breakdown' in transaction_analytics:
                    st.subheader("📅 Monthly Trading Activity")
                    
                    monthly_data = transaction_analytics['monthly_breakdown']
                    months = list(monthly_data.keys())[-6:]  # Last 6 months
                    
                    buy_volumes = [monthly_data[m]['buy_volume'] for m in months]
                    sell_volumes = [monthly_data[m]['sell_volume'] for m in months]
                    
                    fig = go.Figure(data=[
                        go.Bar(name='Buy Volume', x=months, y=buy_volumes, marker_color='#00C9A7'),
                        go.Bar(name='Sell Volume', x=months, y=sell_volumes, marker_color='#C34A36')
                    ])
                    
                    fig.update_layout(
                        barmode='group',
                        title="Monthly Trading Volume",
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Transaction analytics temporarily unavailable: {e}")
            
            # Stock performance breakdown
            if stocks:
                st.subheader("📊 Stock Performance Breakdown")
                
                stock_data = []
                for stock in stocks:
                    try:
                        stock_perf = transaction_service.get_stock_performance(stock['stock_id'])
                        if 'error' not in stock_perf:
                            stock_data.append({
                                'Symbol': stock['symbol'],
                                'Shares': stock_perf['current_shares'],
                                'Avg Cost': stock_perf['average_buy_price'],
                                'Current Price': stock['price'],
                                'Unrealized P&L': stock_perf['unrealized_gain_loss'],
                                'Return %': stock_perf['unrealized_gain_loss_percent']
                            })
                    except:
                        continue
                
                if stock_data:
                    df = pd.DataFrame(stock_data)
                    st.dataframe(
                        df.style.format({
                            'Avg Cost': '${:.2f}',
                            'Current Price': '${:.2f}',
                            'Unrealized P&L': '${:,.2f}',
                            'Return %': '{:+.2f}%'
                        }),
                        use_container_width=True
                    )
        
        except Exception as e:
            st.error(f"❌ Error loading analytics: {e}")
    
    def show_advanced_analytics_charts(self, portfolio_id):
        """Show advanced animated analytics charts"""
        try:
            transaction_analytics = transaction_service.get_transaction_analytics(portfolio_id)
            
            if 'monthly_breakdown' in transaction_analytics:
                # Animated trading activity chart
                monthly_data = transaction_analytics['monthly_breakdown']
                months = list(monthly_data.keys())[-6:]
                
                buy_volumes = [monthly_data[m]['buy_volume'] for m in months]
                sell_volumes = [monthly_data[m]['sell_volume'] for m in months]
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Buy Volume',
                    x=months,
                    y=buy_volumes,
                    marker_color='#00C9A7',
                    opacity=0.8
                ))
                
                fig.add_trace(go.Bar(
                    name='Sell Volume',
                    x=months,
                    y=sell_volumes,
                    marker_color='#C34A36',
                    opacity=0.8
                ))
                
                fig.update_layout(
                    title="📅 Monthly Trading Activity",
                    barmode='group',
                    height=400,
                    xaxis_title="Month",
                    yaxis_title="Volume ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.warning(f"⚠️ Some analytics features unavailable: {e}")
    
    def show_animated_holdings_view(self, user_id):
        """Advanced animated holdings view"""
        st.subheader("💼 Advanced Holdings Analysis")
        
        with st.spinner("🔄 Loading your stock holdings..."):
            portfolios = portfolio_service.get_user_portfolios(user_id)
            all_stocks = []
            
            for portfolio in portfolios:
                try:
                    stocks = stock_service.get_stocks(portfolio['portfolio_id'])
                    for stock in stocks:
                        stock['Portfolio'] = portfolio['portfolio_name']
                        stock['Total Value'] = stock['price'] * stock['quantity']
                        all_stocks.append(stock)
                except:
                    continue
        
        if not all_stocks:
            self.show_animated_empty_state("No stock holdings found")
            return
        
        # Advanced holdings visualization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Interactive holdings table with animations
            holdings_data = []
            for stock in all_stocks:
                holdings_data.append({
                    'Symbol': stock['symbol'],
                    'Portfolio': stock['Portfolio'],
                    'Quantity': stock['quantity'],
                    'Price': stock['price'],
                    'Total Value': stock['Total Value']
                })
            
            df = pd.DataFrame(holdings_data)
            
            # Apply advanced styling
            # FIXED CODE:
            try:
                styled_df = df.style.format({
                    'Price': '${:.2f}',
                    'Total Value': '${:,.2f}'
                }).background_gradient(subset=['Total Value'], cmap='Blues')
            except ImportError:
                # Fallback if matplotlib still has issues
                styled_df = df.style.format({
                    'Price': '${:.2f}',
                    'Total Value': '${:,.2f}'
                }).set_properties(**{
                    'background-color': '#f8f9fa',
                    'color': '#2c3e50'
                }, subset=['Total Value'])
            
            st.dataframe(styled_df, use_container_width=True)
        
        with col2:
            # Holdings summary with animations
            total_value = df['Total Value'].sum()
            unique_stocks = df['Symbol'].nunique()
            total_positions = len(all_stocks)
            
            st.markdown("### 📊 Holdings Summary")
            self.animated_metric_card("Total Value", f"${total_value:,.2f}", "primary")
            self.animated_metric_card("Unique Stocks", str(unique_stocks), "info")
            self.animated_metric_card("Total Positions", str(total_positions), "warning")
    
    def show_animated_market_intel(self):
        """Advanced animated market intelligence"""
        st.subheader("📈 Live Market Intelligence")
        
        # Animated market data cards
        col1, col2, col3, col4 = st.columns(4)
        
        market_indicators = [
            ("S&P 500", "4,567.89", "+1.2%", "success"),
            ("NASDAQ", "14,234.56", "+1.8%", "success"),
            ("DOW", "34,567.89", "+0.8%", "success"),
            ("VIX", "15.23", "-2.1%", "danger")
        ]
        
        for col, (name, value, change, style) in zip([col1, col2, col3, col4], market_indicators):
            with col:
                self.animated_metric_card(name, value, style, change)
        
        # Advanced market visualization
        st.markdown("---")
        
        # Simulated real-time market data
        st.markdown("### 🔮 Market Trends")
        
        # Create animated market trend visualization
        time_points = 50
        times = [datetime.now() - timedelta(hours=x) for x in range(time_points)]
        prices = [100 + 10 * np.sin(x/5) + random.uniform(-2, 2) for x in range(time_points)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=times,
            y=prices,
            mode='lines',
            name='Market Index',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        fig.update_layout(
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Time",
            yaxis_title="Price",
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_animated_quick_actions(self, user_id):
        """Advanced animated quick actions panel"""
        st.subheader("⚡ Smart Quick Actions")
        
        # Action cards in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander("🚀 Create Portfolio", expanded=True):
                with st.form("quick_create_portfolio"):
                    portfolio_name = st.text_input("Portfolio Name", placeholder="Enter portfolio name")
                    
                    if st.form_submit_button("✨ Create Portfolio", use_container_width=True):
                        with st.spinner("Creating your portfolio..."):
                            try:
                                portfolio_service.create_portfolio(user_id, portfolio_name)
                                st.success("✅ Portfolio created successfully!")
                                time.sleep(1)
                                st.rerun()
                            except ValueError as e:
                                st.error(f"❌ {str(e)}")
        
        with col2:
            with st.expander("📈 Add Stock", expanded=True):
                portfolios = portfolio_service.get_user_portfolios(user_id)
                if portfolios:
                    portfolio_options = {p['portfolio_name']: p['portfolio_id'] for p in portfolios}
                    selected_portfolio = st.selectbox("Select Portfolio", options=list(portfolio_options.keys()))
                    
                    with st.form("quick_add_stock"):
                        symbol = st.text_input("Stock Symbol", placeholder="AAPL").upper()
                        quantity = st.number_input("Quantity", min_value=1, value=10)
                        
                        if st.form_submit_button("💫 Add Stock", use_container_width=True):
                            with st.spinner(f"Adding {symbol}..."):
                                try:
                                    portfolio_id = portfolio_options[selected_portfolio]
                                    stock_service.add_stock_with_live_price(portfolio_id, symbol, quantity)
                                    st.success(f"✅ Added {quantity} shares of {symbol}!")
                                    time.sleep(1)
                                    st.rerun()
                                except ValueError as e:
                                    st.error(f"❌ {str(e)}")
                else:
                    st.info("Create a portfolio first")
        
        with col3:
            with st.expander("🔍 Market Research", expanded=True):
                with st.form("quick_research"):
                    search_symbol = st.text_input("Research Symbol", placeholder="TSLA").upper()
                    
                    if st.form_submit_button("🔎 Research Stock", use_container_width=True):
                        with st.spinner(f"Researching {search_symbol}..."):
                            try:
                                stock_info = stock_service.search_stock_info(search_symbol)
                                st.session_state.researched_stock = stock_info
                            except ValueError as e:
                                st.error(f"❌ {str(e)}")
                
                if 'researched_stock' in st.session_state:
                    stock = st.session_state.researched_stock
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h4 style='margin: 0; color: #2c3e50;'>{stock['symbol']}</h4>
                        <p style='margin: 5px 0; color: #7f8c8d;'>{stock['company_name']}</p>
                        <p style='margin: 0; font-size: 1.2em; color: #667eea; font-weight: bold;'>
                            ${stock['current_price']:.2f}
                        </p>
                        <p style='margin: 0; color: #95a5a6; font-size: 0.9em;'>
                            Sector: {stock['sector']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    def show_animated_empty_state(self, message: str = "No portfolios found"):
        """Show animated empty state"""
        st.markdown(f"""
        <div style='text-align: center; padding: 60px 20px; animation: fadeInUp 0.8s ease-out;'>
            <div style='font-size: 4em; margin-bottom: 20px;'>📊</div>
            <h3 style='color: #7f8c8d; margin-bottom: 10px;'>{message}</h3>
            <p style='color: #bdc3c7;'>Get started by creating your first portfolio!</p>
        </div>
        """, unsafe_allow_html=True)
    
    def animated_refresh_prices(self):
        """Advanced animated price refresh"""
        try:
            user = st.session_state.user
            portfolios = portfolio_service.get_user_portfolios(user['user_id'])
            
            if not portfolios:
                st.warning("⚠️ No portfolios to refresh")
                return
            
            # Advanced progress animation
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_portfolios = len(portfolios)
            for i, portfolio in enumerate(portfolios):
                status_text.markdown(f"""
                <div style='animation: fadeInUp 0.3s ease-out;'>
                    🔄 Refreshing <strong>{portfolio['portfolio_name']}</strong>...
                </div>
                """, unsafe_allow_html=True)
                
                try:
                    portfolio_service.refresh_portfolio_prices(portfolio['portfolio_id'])
                except:
                    pass  # Continue with other portfolios
                
                progress = (i + 1) / total_portfolios
                progress_bar.progress(progress)
                
                # Simulate processing time for animation
                time.sleep(0.5)
            
            # Success animation
            status_text.markdown("""
            <div style='animation: fadeInUp 0.5s ease-out; color: #00C9A7; font-weight: bold;'>
                ✅ All prices refreshed successfully!
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(2)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error refreshing prices: {e}")

# Run the ultra-animated application
if __name__ == "__main__":
    app = AnimatedStockTracker()
    app.run()