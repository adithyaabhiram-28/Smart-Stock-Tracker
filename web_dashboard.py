import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf

# Import your existing services
from Service.user_service import UserService
from Service.portfolio_service import PortfolioService
from Service.stock_service import StockService
from Service.transaction_service import TransactionService

# Page configuration
st.set_page_config(
    page_title="Smart Stock Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
user_service = UserService()
portfolio_service = PortfolioService()
stock_service = StockService()
transaction_service = TransactionService()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .portfolio-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .positive-change {
        color: #00cc96;
        font-weight: bold;
    }
    .negative-change {
        color: #ef553b;
        font-weight: bold;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def login_section():
    """Handle user login and registration"""
    st.sidebar.title("🔐 Authentication")
    
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        login_email = st.text_input("Email", key="login_email")
        
        if st.button("Login", key="login_btn"):
            if login_email:
                user = user_service.user_dao.get_user_by_email(login_email)
                if user:
                    st.session_state.user = user
                    st.session_state.current_portfolio = None
                    st.rerun()
                else:
                    st.error("❌ User not found. Please check your email or register.")
            else:
                st.warning("Please enter your email")
    
    with tab2:
        st.subheader("Create New Account")
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        
        if st.button("Register", key="reg_btn"):
            if reg_name and reg_email:
                try:
                    user_service.register_user(reg_name, reg_email)
                    st.success("✅ Account created successfully! Please login.")
                except ValueError as e:
                    st.error(f"❌ {e}")
            else:
                st.warning("Please fill all fields")

def logout_section():
    """Handle user logout"""
    if st.sidebar.button("🚪 Logout"):
        if 'user' in st.session_state:
            del st.session_state.user
        if 'current_portfolio' in st.session_state:
            del st.session_state.current_portfolio
        st.rerun()

def dashboard_overview():
    """Main dashboard with portfolio overview"""
    st.markdown('<div class="main-header">💰 Smart Stock Tracker</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    portfolios = portfolio_service.get_user_portfolios(st.session_state.user['user_id'])
    total_value = 0
    total_gain_loss = 0
    total_stocks = 0
    
    if portfolios:
        portfolio_summaries = portfolio_service.get_portfolio_summary(st.session_state.user['user_id'])
        
        for summary in portfolio_summaries:
            if 'error' not in summary:
                total_value += summary['current_value']
                total_gain_loss += summary['total_gain_loss']
                total_stocks += summary['stock_count']
    
    with col1:
        st.metric("Total Net Worth", f"${total_value:,.2f}")
    with col2:
        gain_color = "normal" if total_gain_loss >= 0 else "inverse"
        st.metric("Total Gain/Loss", f"${total_gain_loss:,.2f}", delta=f"{total_gain_loss:,.2f}", delta_color=gain_color)
    with col3:
        st.metric("Portfolios", len(portfolios))
    with col4:
        st.metric("Total Stocks", total_stocks)
    
    # Refresh all prices
    if st.button("🔄 Refresh All Portfolio Prices"):
        with st.spinner("Refreshing prices..."):
            total_updated = 0
            for portfolio in portfolios:
                try:
                    result = portfolio_service.refresh_portfolio_prices(portfolio['portfolio_id'])
                    total_updated += result['stocks_updated']
                except:
                    continue
            st.success(f"✅ Updated {total_updated} stock prices!")
            st.rerun()
    
    st.markdown("---")
    
    # Portfolio cards
    if portfolios:
        st.subheader("📁 Your Portfolios")
        
        for portfolio in portfolios:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"### {portfolio['portfolio_name']}")
                    st.write(f"*ID: {portfolio['portfolio_id']}*")
                
                try:
                    analytics = portfolio_service.get_portfolio_analytics(portfolio['portfolio_id'])
                    performance = analytics['performance']
                    
                    with col2:
                        st.metric("Current Value", f"${performance['current_value']:,.2f}")
                    
                    with col3:
                        gain_loss = performance['total_gain_loss']
                        gain_color = "normal" if gain_loss >= 0 else "inverse"
                        st.metric("Gain/Loss", f"${gain_loss:,.2f}", 
                                 delta=f"{performance['gain_loss_percentage']:+.2f}%", 
                                 delta_color=gain_color)
                    
                    with col4:
                        if st.button("Manage", key=f"manage_{portfolio['portfolio_id']}"):
                            st.session_state.current_portfolio = portfolio
                            st.rerun()
                
                except Exception as e:
                    with col2:
                        st.write("Error loading analytics")
                    with col3:
                        st.write("—")
                    with col4:
                        if st.button("Manage", key=f"manage_{portfolio['portfolio_id']}"):
                            st.session_state.current_portfolio = portfolio
                            st.rerun()
        
        st.markdown("---")
        
        # Portfolio performance chart
        st.subheader("📊 Portfolio Performance")
        
        portfolio_data = []
        for portfolio in portfolios:
            try:
                analytics = portfolio_service.get_portfolio_analytics(portfolio['portfolio_id'])
                performance = analytics['performance']
                portfolio_data.append({
                    'Portfolio': portfolio['portfolio_name'],
                    'Current Value': performance['current_value'],
                    'Gain/Loss': performance['total_gain_loss'],
                    'Return %': performance['gain_loss_percentage']
                })
            except:
                continue
        
        if portfolio_data:
            df = pd.DataFrame(portfolio_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Value chart
                fig_value = px.bar(df, x='Portfolio', y='Current Value', 
                                 title="Portfolio Values", color='Current Value',
                                 color_continuous_scale='Viridis')
                st.plotly_chart(fig_value, use_container_width=True)
            
            with col2:
                # Return chart
                fig_return = px.bar(df, x='Portfolio', y='Return %',
                                  title="Portfolio Returns (%)", 
                                  color='Return %', 
                                  color_continuous_scale='RdYlGn')
                st.plotly_chart(fig_return, use_container_width=True)
    
    else:
        st.info("No portfolios found. Create your first portfolio to get started!")

def portfolio_management():
    """Portfolio creation and management"""
    st.sidebar.subheader("📊 Portfolio Management")
    
    # Create new portfolio
    with st.sidebar.form("create_portfolio"):
        st.write("### Create New Portfolio")
        new_portfolio_name = st.text_input("Portfolio Name")
        create_btn = st.form_submit_button("Create Portfolio")
        
        if create_btn and new_portfolio_name:
            try:
                portfolio_service.create_portfolio(st.session_state.user['user_id'], new_portfolio_name)
                st.sidebar.success("✅ Portfolio created successfully!")
                st.rerun()
            except ValueError as e:
                st.sidebar.error(f"❌ {e}")
    
    st.sidebar.markdown("---")
    
    # Portfolio list in sidebar
    portfolios = portfolio_service.get_user_portfolios(st.session_state.user['user_id'])
    if portfolios:
        st.sidebar.write("### Your Portfolios")
        for portfolio in portfolios:
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.write(portfolio['portfolio_name'])
            with col2:
                if st.button("Select", key=f"select_{portfolio['portfolio_id']}"):
                    st.session_state.current_portfolio = portfolio
                    st.rerun()

def portfolio_detail_view():
    """Detailed view for a specific portfolio"""
    portfolio = st.session_state.current_portfolio
    
    st.markdown(f'<div class="main-header">🎯 {portfolio["portfolio_name"]}</div>', unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_portfolio = None
        st.rerun()
    
    # Portfolio analytics
    try:
        analytics = portfolio_service.get_portfolio_analytics(portfolio['portfolio_id'])
        performance = analytics['performance']
        stocks = analytics['stocks']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Invested", f"${performance['total_invested']:,.2f}")
        with col2:
            st.metric("Current Value", f"${performance['current_value']:,.2f}")
        with col3:
            gain_loss = performance['total_gain_loss']
            gain_color = "normal" if gain_loss >= 0 else "inverse"
            st.metric("Total Gain/Loss", f"${gain_loss:,.2f}", 
                     delta=f"{performance['gain_loss_percentage']:+.2f}%", 
                     delta_color=gain_color)
        with col4:
            st.metric("Stocks Held", len(stocks))
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Refresh Prices"):
                with st.spinner("Refreshing prices..."):
                    result = portfolio_service.refresh_portfolio_prices(portfolio['portfolio_id'])
                    st.success(f"✅ Updated {result['stocks_updated']} stock prices!")
                    st.rerun()
        with col2:
            if st.button("📈 View Analytics"):
                st.session_state.show_analytics = True
                st.rerun()
        with col3:
            if st.button("🗑️ Delete Portfolio"):
                st.warning("This will delete ALL stocks and transactions in this portfolio!")
                if st.button("CONFIRM DELETE", type="primary"):
                    portfolio_service.delete_portfolio(portfolio['portfolio_id'])
                    st.session_state.current_portfolio = None
                    st.success("✅ Portfolio deleted successfully!")
                    st.rerun()
        
        st.markdown("---")
        
        # Stock management
        st.subheader("📦 Stock Holdings")
        
        if stocks:
            # Display stocks in a table
            stock_data = []
            total_portfolio_value = 0
            
            for stock in stocks:
                stock_value = stock['price'] * stock['quantity']
                total_portfolio_value += stock_value
                stock_data.append({
                    'Symbol': stock['symbol'],
                    'Quantity': stock['quantity'],
                    'Current Price': f"${stock['price']:.2f}",
                    'Total Value': f"${stock_value:,.2f}",
                    'Stock ID': stock['stock_id']
                })
            
            df = pd.DataFrame(stock_data)
            st.dataframe(df, use_container_width=True)
            
            # Stock actions
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("➕ Add New Stock"):
                    add_stock_form(stocks)
            
            with col2:
                with st.expander("✏️ Update/Delete Stock"):
                    update_delete_stock_form(stocks)
        
        else:
            st.info("No stocks in this portfolio. Add your first stock!")
            with st.expander("➕ Add New Stock"):
                add_stock_form([])
        
        # Transactions
        st.markdown("---")
        st.subheader("💰 Recent Transactions")
        
        try:
            transactions = transaction_service.get_portfolio_transactions(portfolio['portfolio_id'])
            if transactions:
                trans_data = []
                for trans in transactions[:10]:  # Show last 10 transactions
                    stock_data = stock_service.stock_dao.get_stock_by_id(trans['stock_id'])
                    symbol = stock_data[0]['symbol'] if stock_data else "Unknown"
                    
                    trans_data.append({
                        'Date': trans.get('date', '')[:10],
                        'Type': trans['type'],
                        'Symbol': symbol,
                        'Quantity': trans['quantity'],
                        'Price': f"${trans['price']:.2f}",
                        'Total': f"${trans['quantity'] * trans['price']:,.2f}"
                    })
                
                trans_df = pd.DataFrame(trans_data)
                st.dataframe(trans_df, use_container_width=True)
            else:
                st.info("No transactions yet.")
        
        except Exception as e:
            st.error(f"Error loading transactions: {e}")
    
    except Exception as e:
        st.error(f"Error loading portfolio details: {e}")

def add_stock_form(existing_stocks):
    """Form to add new stocks"""
    with st.form("add_stock"):
        symbol = st.text_input("Stock Symbol (e.g., AAPL)", key="add_symbol").upper()
        use_live_price = st.checkbox("Use live market price", value=True)
        
        if use_live_price:
            quantity = st.number_input("Quantity", min_value=1, value=1)
            price = None
        else:
            quantity = st.number_input("Quantity", min_value=1, value=1)
            price = st.number_input("Price per share ($)", min_value=0.01, value=100.0)
        
        submitted = st.form_submit_button("Add Stock")
        
        if submitted and symbol:
            try:
                if use_live_price:
                    # Show stock info before adding
                    stock_info = stock_service.search_stock_info(symbol)
                    st.success(f"✅ {stock_info['company_name']} - Current Price: ${stock_info['current_price']:.2f}")
                    
                    confirm = st.button(f"Confirm Add {quantity} shares of {symbol}")
                    if confirm:
                        stock_service.add_stock_with_live_price(
                            st.session_state.current_portfolio['portfolio_id'], 
                            symbol, quantity
                        )
                        st.success("✅ Stock added successfully!")
                        st.rerun()
                else:
                    stock_service.add_stock(
                        st.session_state.current_portfolio['portfolio_id'],
                        symbol, price, quantity
                    )
                    st.success("✅ Stock added successfully!")
                    st.rerun()
            except ValueError as e:
                st.error(f"❌ {e}")

def update_delete_stock_form(stocks):
    """Form to update or delete stocks"""
    if stocks:
        stock_options = {f"{s['symbol']} (ID: {s['stock_id']})": s['stock_id'] for s in stocks}
        selected_stock = st.selectbox("Select Stock", list(stock_options.keys()))
        
        if selected_stock:
            stock_id = stock_options[selected_stock]
            stock_data = stock_service.stock_dao.get_stock_by_id(stock_id)
            
            if stock_data:
                stock = stock_data[0]
                st.write(f"Current: {stock['symbol']} - Qty: {stock['quantity']} - Price: ${stock['price']:.2f}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_quantity = st.number_input("New Quantity", value=stock['quantity'], min_value=0)
                with col2:
                    new_price = st.number_input("New Price ($)", value=float(stock['price']), min_value=0.01)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Stock"):
                        try:
                            stock_service.update_stock(stock_id, new_price, new_quantity)
                            st.success("✅ Stock updated successfully!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ {e}")
                
                with col2:
                    if st.button("Delete Stock", type="secondary"):
                        try:
                            stock_service.delete_stock(stock_id)
                            st.success("✅ Stock deleted successfully!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ {e}")

def market_watch():
    """Market watch and stock search"""
    st.sidebar.subheader("📈 Market Watch")
    
    st.markdown('<div class="main-header">📈 Market Watch</div>', unsafe_allow_html=True)
    
    # Popular stocks
    st.subheader("🔥 Popular Stocks")
    popular_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
    
    cols = st.columns(4)
    for i, symbol in enumerate(popular_stocks):
        with cols[i % 4]:
            try:
                stock_info = stock_service.search_stock_info(symbol)
                current_price = stock_info['current_price']
                prev_close = stock_info['previous_close']
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100
                
                st.metric(
                    symbol,
                    f"${current_price:.2f}",
                    delta=f"{change:+.2f} ({change_percent:+.1f}%)",
                    delta_color="normal" if change >= 0 else "inverse"
                )
            except:
                st.metric(symbol, "N/A")
    
    st.markdown("---")
    
    # Stock search
    st.subheader("🔍 Stock Search")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_symbol = st.text_input("Enter stock symbol", key="search_symbol").upper()
    
    with col2:
        st.write("")  # Spacing
        search_btn = st.button("Search", key="search_btn")
    
    if search_btn and search_symbol:
        with st.spinner(f"Searching for {search_symbol}..."):
            try:
                stock_info = stock_service.search_stock_info(search_symbol)
                
                st.success(f"✅ Found: {stock_info['company_name']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Company Information")
                    st.write(f"**Symbol:** {stock_info['symbol']}")
                    st.write(f"**Sector:** {stock_info['sector']}")
                    st.write(f"**Industry:** {stock_info['industry']}")
                    st.write(f"**Market Cap:** ${stock_info['market_cap']:,.0f}")
                
                with col2:
                    st.subheader("Price Data")
                    st.write(f"**Current Price:** ${stock_info['current_price']:.2f}")
                    st.write(f"**Previous Close:** ${stock_info['previous_close']:.2f}")
                    
                    change = stock_info['current_price'] - stock_info['previous_close']
                    change_percent = (change / stock_info['previous_close']) * 100
                    
                    st.write(f"**Change:** ${change:+.2f} ({change_percent:+.2f}%)")
                
                st.subheader("Company Description")
                st.write(stock_info['description'])
                
                # Quick add to portfolio
                st.markdown("---")
                st.subheader("💼 Add to Portfolio")
                
                portfolios = portfolio_service.get_user_portfolios(st.session_state.user['user_id'])
                if portfolios:
                    portfolio_options = {p['portfolio_name']: p['portfolio_id'] for p in portfolios}
                    selected_portfolio = st.selectbox("Select Portfolio", list(portfolio_options.keys()))
                    quantity = st.number_input("Quantity", min_value=1, value=1)
                    
                    if st.button(f"Add {quantity} shares to {selected_portfolio}"):
                        try:
                            portfolio_id = portfolio_options[selected_portfolio]
                            stock_service.add_stock_with_live_price(portfolio_id, search_symbol, quantity)
                            st.success(f"✅ Added {quantity} shares of {search_symbol} to {selected_portfolio}!")
                        except ValueError as e:
                            st.error(f"❌ {e}")
                else:
                    st.info("No portfolios available. Create a portfolio first!")
                
            except ValueError as e:
                st.error(f"❌ {e}")

def analytics_dashboard():
    """Advanced analytics and insights"""
    st.markdown('<div class="main-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    portfolios = portfolio_service.get_user_portfolios(st.session_state.user['user_id'])
    
    if not portfolios:
        st.info("No portfolios available for analytics.")
        return
    
    # Portfolio selection for detailed analytics
    portfolio_options = {p['portfolio_name']: p['portfolio_id'] for p in portfolios}
    selected_portfolio_name = st.selectbox("Select Portfolio for Detailed Analytics", list(portfolio_options.keys()))
    
    if selected_portfolio_name:
        portfolio_id = portfolio_options[selected_portfolio_name]
        
        try:
            analytics = portfolio_service.get_portfolio_analytics(portfolio_id)
            performance = analytics['performance']
            stocks = analytics['stocks']
            transaction_analytics = transaction_service.get_transaction_analytics(portfolio_id)
            
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Invested", f"${performance['total_invested']:,.2f}")
            with col2:
                st.metric("Current Value", f"${performance['current_value']:,.2f}")
            with col3:
                st.metric("Total Return", f"${performance['total_gain_loss']:,.2f}")
            with col4:
                st.metric("Return %", f"{performance['gain_loss_percentage']:+.2f}%")
            
            st.markdown("---")
            
            # Stock allocation pie chart
            if stocks:
                st.subheader("📊 Stock Allocation")
                
                stock_values = []
                for stock in stocks:
                    value = stock['price'] * stock['quantity']
                    stock_values.append({
                        'Symbol': stock['symbol'],
                        'Value': value,
                        'Percentage': (value / performance['current_value']) * 100
                    })
                
                df_allocation = pd.DataFrame(stock_values)
                
                fig_pie = px.pie(df_allocation, values='Value', names='Symbol', 
                               title="Portfolio Allocation by Stock")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Transaction analytics
            if 'monthly_breakdown' in transaction_analytics:
                st.subheader("📅 Monthly Trading Activity")
                
                monthly_data = transaction_analytics['monthly_breakdown']
                if monthly_data:
                    months = list(monthly_data.keys())
                    buy_volumes = [monthly_data[m]['buy_volume'] for m in months]
                    sell_volumes = [monthly_data[m]['sell_volume'] for m in months]
                    
                    fig_volume = go.Figure(data=[
                        go.Bar(name='Buy Volume', x=months, y=buy_volumes),
                        go.Bar(name='Sell Volume', x=months, y=sell_volumes)
                    ])
                    fig_volume.update_layout(barmode='group', title="Monthly Trading Volume")
                    st.plotly_chart(fig_volume, use_container_width=True)
            
            # Most traded stocks
            if 'most_traded_stocks' in transaction_analytics:
                st.subheader("🏆 Most Traded Stocks")
                
                most_traded = transaction_analytics['most_traded_stocks']
                if most_traded:
                    traded_df = pd.DataFrame(most_traded)
                    st.dataframe(traded_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error loading analytics: {e}")

def main():
    """Main application flow"""
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        # Show login page
        st.markdown('<div class="main-header">💰 Smart Stock Tracker</div>', unsafe_allow_html=True)
        st.markdown("### Your All-in-One Investment Tracking Solution")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            #### 📈 Features:
            - **Real-time Portfolio Tracking** - Live stock prices and performance
            - **Comprehensive Analytics** - Gain/loss calculations and ROI metrics
            - **Market Watch** - Real-time stock search and trends
            - **Transaction History** - Complete buy/sell tracking
            - **Professional Dashboard** - Clean, intuitive interface
            
            #### 🚀 Get Started:
            1. Register with your email
            2. Create your first portfolio
            3. Add stocks with live prices
            4. Track your investments in real-time
            """)
        
        with col2:
            login_section()
    
    else:
        # User is logged in - show main application
        user = st.session_state.user
        st.sidebar.success(f"👋 Welcome, **{user['name']}**!")
        
        # Logout section
        logout_section()
        
        # Portfolio management in sidebar
        portfolio_management()
        
        # Main navigation
        st.sidebar.markdown("---")
        st.sidebar.subheader("📱 Navigation")
        
        nav_options = ["Dashboard", "Market Watch", "Analytics"]
        selected_nav = st.sidebar.radio("Go to", nav_options)
        
        # Show current portfolio in sidebar if selected
        if 'current_portfolio' in st.session_state and st.session_state.current_portfolio:
            st.sidebar.markdown("---")
            st.sidebar.info(f"**Current Portfolio:** {st.session_state.current_portfolio['portfolio_name']}")
        
        # Main content based on navigation
        if 'current_portfolio' in st.session_state and st.session_state.current_portfolio:
            portfolio_detail_view()
        elif selected_nav == "Dashboard":
            dashboard_overview()
        elif selected_nav == "Market Watch":
            market_watch()
        elif selected_nav == "Analytics":
            analytics_dashboard()

if __name__ == "__main__":
    main()