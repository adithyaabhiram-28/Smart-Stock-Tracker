from DAO.portfolio_dao import PortfolioDAO
from DAO.stock_dao import StockDAO
from Service.stock_service import StockService
from Service.transaction_service import TransactionService

class PortfolioService:
    def __init__(self):
        self.portfolio_dao = PortfolioDAO()
        self.stock_service = StockService()
        self.transaction_service = TransactionService()
    
    def create_portfolio(self, user_id, portfolio_name):
        existing = self.portfolio_dao.get_portfolio_by_user(user_id)
        if any(p["portfolio_name"] == portfolio_name for p in existing):
            raise ValueError("Portfolio already exists")
        return self.portfolio_dao.create_portfolio(user_id, portfolio_name)
    
    def get_user_portfolios(self, user_id):
        return self.portfolio_dao.get_portfolio_by_user(user_id)
    
    def update_portfolio(self, portfolio_id, portfolio_name):
        return self.portfolio_dao.update_portfolio(portfolio_id, portfolio_name)
    
    def delete_portfolio(self, portfolio_id):
        portfolio = self.portfolio_dao.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        return self.portfolio_dao.delete_portfolio(portfolio_id)
    
    def get_portfolio_analytics(self, portfolio_id):
        """Get comprehensive portfolio analytics and performance metrics - FIXED"""
        portfolio = self.portfolio_dao.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        # Get performance data from transaction service
        performance = self.transaction_service.get_portfolio_performance(portfolio_id)
        
        # Get current stocks
        stocks = self.stock_service.get_stocks(portfolio_id)
        
        # Calculate additional metrics
        if stocks:
            # Find top performing stock
            top_stock = max(stocks, key=lambda s: s['price'] * s['quantity'])
            # Find stock with highest quantity
            highest_quantity = max(stocks, key=lambda s: s['quantity'])
        else:
            top_stock = None
            highest_quantity = None
        
        return {
            'portfolio_info': portfolio,
            'performance': performance,
            'stocks': stocks,
            'stock_count': len(stocks),
            'top_stock': top_stock,
            'highest_quantity_stock': highest_quantity
        }
    
    def refresh_portfolio_prices(self, portfolio_id):
        """Refresh all stock prices in portfolio with live data"""
        portfolio = self.portfolio_dao.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        updated_count = self.stock_service.refresh_stock_prices(portfolio_id)
        return {
            'portfolio_name': portfolio['portfolio_name'],
            'stocks_updated': updated_count
        }
    
    def get_portfolio_summary(self, user_id):
        """Get summary of all portfolios for a user with their total values - FIXED"""
        portfolios = self.get_user_portfolios(user_id)
        portfolio_summaries = []
        
        for portfolio in portfolios:
            try:
                # Use transaction service for performance data
                performance = self.transaction_service.get_portfolio_performance(portfolio['portfolio_id'])
                stocks = self.stock_service.get_stocks(portfolio['portfolio_id'])
                
                portfolio_summaries.append({
                    'portfolio_id': portfolio['portfolio_id'],
                    'portfolio_name': portfolio['portfolio_name'],
                    'current_value': performance['current_value'],
                    'total_gain_loss': performance['total_gain_loss'],
                    'gain_loss_percentage': performance['gain_loss_percentage'],
                    'stock_count': len(stocks)
                })
            except Exception as e:
                # If analytics fail, provide basic info
                portfolio_summaries.append({
                    'portfolio_id': portfolio['portfolio_id'],
                    'portfolio_name': portfolio['portfolio_name'],
                    'current_value': 0,
                    'total_gain_loss': 0,
                    'gain_loss_percentage': 0,
                    'stock_count': 0,
                    'error': str(e)
                })
        
        return portfolio_summaries