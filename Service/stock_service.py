import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DAO.stock_dao import StockDAO
import yfinance as yf
from datetime import datetime

class StockService:
    def __init__(self):
        self.stock_dao = StockDAO()
    
    def get_live_price(self, symbol):
        """Fetch live stock price from Yahoo Finance with enhanced error handling"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Try multiple price fields with fallbacks
            current_price = (info.get('currentPrice') or 
                           info.get('regularMarketPrice') or
                           info.get('previousClose') or
                           info.get('open'))
            
            if not current_price:
                # Fallback to historical data
                hist = stock.history(period="1d")
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            price_float = float(current_price)
            if price_float <= 0:
                raise ValueError(f"Invalid price for {symbol}")
                
            return price_float
            
        except Exception as e:
            raise ValueError(f"Could not fetch price for {symbol}: {str(e)}")
    
    def add_stock(self, portfolio_id, symbol, quantity, price=None):
        """Add stock with optional live price fetching and quantity updates"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        symbol = symbol.upper()
        
        # Use provided price or fetch live price
        if price is None:
            price = self.get_live_price(symbol)
        elif price <= 0:
            raise ValueError("Price must be positive")
        
        # Check for existing stock in portfolio
        existing_stocks = self.stock_dao.get_stock_by_portfolio(portfolio_id)
        for stock in existing_stocks:
            if stock["symbol"] == symbol:
                # Update existing stock quantity and price
                new_quantity = stock["quantity"] + quantity
                return self.stock_dao.update_stock(stock["stock_id"], price=price, quantity=new_quantity)
        
        # Add new stock
        return self.stock_dao.add_stock(portfolio_id, symbol, price, quantity)
    
    def add_stock_with_live_price(self, portfolio_id, symbol, quantity):
        """Convenience method specifically for live price addition"""
        return self.add_stock(portfolio_id, symbol, quantity, price=None)
    
    def get_stocks(self, portfolio_id):
        """Get all stocks in portfolio with additional calculated fields"""
        stocks = self.stock_dao.get_stock_by_portfolio(portfolio_id)
        
        # Add calculated fields for convenience
        for stock in stocks:
            stock['total_value'] = stock['price'] * stock['quantity']
        
        return stocks
    
    def get_portfolio_value(self, portfolio_id):
        """Calculate total value of all stocks in portfolio"""
        stocks = self.get_stocks(portfolio_id)
        return sum(stock['total_value'] for stock in stocks)
    
    def refresh_stock_prices(self, portfolio_id):
        """Refresh all stock prices in portfolio with live data"""
        stocks = self.get_stocks(portfolio_id)
        updated_count = 0
        
        for stock in stocks:
            try:
                live_price = self.get_live_price(stock['symbol'])
                self.stock_dao.update_stock(stock['stock_id'], price=live_price)
                updated_count += 1
            except ValueError:
                continue  # Skip if we can't get live price, keep existing price
        
        return updated_count
    
    def refresh_single_stock_price(self, stock_id):
        """Refresh price for a single stock"""
        stock_data = self.stock_dao.get_stock_by_id(stock_id)
        if not stock_data:
            raise ValueError("Stock not found")
        
        stock = stock_data[0]
        try:
            live_price = self.get_live_price(stock['symbol'])
            self.stock_dao.update_stock(stock_id, price=live_price)
            return live_price
        except ValueError as e:
            raise ValueError(f"Could not refresh price for {stock['symbol']}: {str(e)}")
    
    def update_stock(self, stock_id, price=None, quantity=None):
        """Update stock with validation"""
        if price is not None and price <= 0:
            raise ValueError("Price must be positive")
        if quantity is not None and quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        return self.stock_dao.update_stock(stock_id, price, quantity)
    
    def delete_stock(self, stock_id):
        """Delete stock with existence check"""
        stock = self.stock_dao.get_stock_by_id(stock_id)
        if not stock:
            raise ValueError("Stock not found")
        return self.stock_dao.delete_stock(stock_id)
    
    def get_stock_performance(self, stock_id):
        """Calculate basic performance metrics for a stock"""
        stock_data = self.stock_dao.get_stock_by_id(stock_id)
        if not stock_data:
            raise ValueError("Stock not found")
        
        stock = stock_data[0]
        total_value = stock['price'] * stock['quantity']
        
        return {
            'symbol': stock['symbol'],
            'quantity': stock['quantity'],
            'current_price': stock['price'],
            'total_value': total_value,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def search_stock_info(self, symbol):
        """Get detailed information about a stock symbol"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                'symbol': symbol.upper(),
                'company_name': info.get('longName', 'N/A'),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'previous_close': info.get('previousClose', 0),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'description': info.get('longBusinessSummary', '')[:200] + '...'  # Truncate long descriptions
            }
        except Exception as e:
            raise ValueError(f"Could not fetch information for {symbol}: {str(e)}")