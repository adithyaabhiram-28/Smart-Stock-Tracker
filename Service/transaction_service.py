from DAO.transaction_dao import TransactionDAO
from DAO.stock_dao import StockDAO
from DAO.portfolio_dao import PortfolioDAO
from datetime import datetime, timedelta

class TransactionService:
    def __init__(self):
        self.trans_dao = TransactionDAO()
        self.stock_dao = StockDAO()
        self.portfolio_dao = PortfolioDAO()

    def buy_stock(self, portfolio_id, stock_id, quantity, price):
        """Buy a stock: record transaction and increase stock quantity"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")

        # Get existing stock
        stock_data = self.stock_dao.get_stock_by_id(stock_id)
        if not stock_data:
            raise ValueError("Stock not found in portfolio")
        
        stock = stock_data[0]

        # Update stock quantity ONLY (preserve original purchase price for tracking)
        new_qty = stock['quantity'] + quantity
        self.stock_dao.update_stock(stock_id, quantity=new_qty)

        # Add transaction
        return self.trans_dao.add_transaction(portfolio_id, stock_id, "Buy", quantity, price)

    def sell_stock(self, portfolio_id, stock_id, quantity, price):
        """Sell a stock: record transaction and decrease stock quantity"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")

        # Get existing stock
        stock_data = self.stock_dao.get_stock_by_id(stock_id)
        if not stock_data:
            raise ValueError("Stock not found in portfolio")

        stock = stock_data[0]
        current_qty = stock['quantity']
        
        if quantity > current_qty:
            raise ValueError(f"Cannot sell {quantity} shares, only {current_qty} available")

        # Update stock quantity or delete if zero
        new_qty = current_qty - quantity
        if new_qty == 0:
            self.stock_dao.delete_stock(stock_id)
        else:
            self.stock_dao.update_stock(stock_id, quantity=new_qty)

        # Add transaction
        return self.trans_dao.add_transaction(portfolio_id, stock_id, "Sell", quantity, price)

    def get_portfolio_transactions(self, portfolio_id):
        """Get all transactions for a portfolio with enhanced sorting"""
        transactions = self.trans_dao.get_transactions_by_portfolio(portfolio_id)
        # Sort by date descending (most recent first)
        return sorted(transactions, key=lambda x: x.get('date', ''), reverse=True)

    def get_stock_transactions(self, stock_id):
        """Get all transactions for a stock"""
        return self.trans_dao.get_transactions_by_stock(stock_id)
    
    def get_portfolio_performance(self, portfolio_id):
        """Calculate comprehensive portfolio performance metrics - FIXED VERSION"""
        transactions = self.get_portfolio_transactions(portfolio_id)
        
        total_invested = 0
        total_sold = 0
        buy_volume = 0
        sell_volume = 0
        transaction_count = len(transactions)
        
        # Calculate from transactions
        for trans in transactions:
            trans_value = trans['quantity'] * trans['price']
            if trans['type'] == 'Buy':
                total_invested += trans_value
                buy_volume += trans_value
            else:  # Sell
                total_sold += trans_value
                sell_volume += trans_value
        
        # Calculate current holdings value - FIXED: Handle empty stocks case
        stocks = self.stock_dao.get_stock_by_portfolio(portfolio_id)
        current_holdings_value = 0
        if stocks:  # Added safety check
            for stock in stocks:
                current_holdings_value += stock['quantity'] * stock['price']
        
        # Calculate performance metrics
        net_value = current_holdings_value + total_sold
        total_gain_loss = net_value - total_invested
        gain_loss_percentage = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        # Calculate recent activity (last 30 days)
        recent_transactions = self._get_recent_transactions(transactions, days=30)
        
        return {
            'total_invested': total_invested,
            'current_holdings_value': current_holdings_value,
            'current_value': current_holdings_value,  # FIXED: Changed key name
            'total_sold': total_sold,
            'net_value': net_value,
            'total_gain_loss': total_gain_loss,
            'gain_loss_percentage': gain_loss_percentage,
            'transaction_count': transaction_count,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'recent_activity': len(recent_transactions),
            'stocks_held': len(stocks) if stocks else 0
        }
    
    def _get_recent_transactions(self, transactions, days=30):
        """Get transactions from the last N days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent = []
            for trans in transactions:
                trans_date = trans.get('date')
                if trans_date:
                    # Convert string to datetime if needed
                    if isinstance(trans_date, str):
                        trans_date = datetime.fromisoformat(trans_date.replace('Z', '+00:00'))
                    if trans_date >= cutoff_date:
                        recent.append(trans)
            return recent
        except:
            return []

    def get_transaction_analytics(self, portfolio_id):
        """Get detailed transaction analytics and trends"""
        transactions = self.get_portfolio_transactions(portfolio_id)
        
        if not transactions:
            return {"error": "No transactions found"}
        
        # Group by month
        monthly_data = {}
        for trans in transactions:
            trans_date = trans.get('date')
            if trans_date:
                try:
                    if isinstance(trans_date, str):
                        trans_date = datetime.fromisoformat(trans_date.replace('Z', '+00:00'))
                    month_key = trans_date.strftime('%Y-%m')
                    
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {'buys': 0, 'sells': 0, 'buy_volume': 0, 'sell_volume': 0}
                    
                    trans_value = trans['quantity'] * trans['price']
                    if trans['type'] == 'Buy':
                        monthly_data[month_key]['buys'] += 1
                        monthly_data[month_key]['buy_volume'] += trans_value
                    else:
                        monthly_data[month_key]['sells'] += 1
                        monthly_data[month_key]['sell_volume'] += trans_value
                except Exception as e:
                    continue
        
        # Most traded stocks
        stock_trades = {}
        for trans in transactions:
            stock_id = trans['stock_id']
            if stock_id not in stock_trades:
                # Get stock symbol
                try:
                    stock_data = self.stock_dao.get_stock_by_id(stock_id)
                    symbol = stock_data[0]['symbol'] if stock_data else f"Stock_{stock_id}"
                    stock_trades[stock_id] = {'symbol': symbol, 'buys': 0, 'sells': 0, 'volume': 0}
                except:
                    stock_trades[stock_id] = {'symbol': f"Stock_{stock_id}", 'buys': 0, 'sells': 0, 'volume': 0}
            
            trans_value = trans['quantity'] * trans['price']
            if trans['type'] == 'Buy':
                stock_trades[stock_id]['buys'] += 1
            else:
                stock_trades[stock_id]['sells'] += 1
            stock_trades[stock_id]['volume'] += trans_value
        
        # Sort by volume
        most_traded = sorted(stock_trades.values(), key=lambda x: x['volume'], reverse=True)[:5]
        
        return {
            'monthly_breakdown': monthly_data,
            'most_traded_stocks': most_traded,
            'total_transactions': len(transactions),
            'buy_sell_ratio': self._calculate_buy_sell_ratio(transactions)
        }
    
    def _calculate_buy_sell_ratio(self, transactions):
        """Calculate buy vs sell ratio"""
        buys = sum(1 for t in transactions if t['type'] == 'Buy')
        sells = sum(1 for t in transactions if t['type'] == 'Sell')
        total = buys + sells
        if total == 0:
            return {'buy_ratio': 0, 'sell_ratio': 0}
        return {
            'buy_ratio': (buys / total) * 100,
            'sell_ratio': (sells / total) * 100
        }
    
    def get_stock_performance(self, stock_id):
        """Calculate performance for a specific stock - FIXED VERSION"""
        transactions = self.get_stock_transactions(stock_id)
        stock_data = self.stock_dao.get_stock_by_id(stock_id)
        
        if not stock_data or not transactions:
            return {"error": "No data available"}
        
        stock = stock_data[0]
        total_shares_bought = 0
        total_shares_sold = 0
        total_cost = 0
        total_proceeds = 0
        
        for trans in transactions:
            if trans['type'] == 'Buy':
                total_shares_bought += trans['quantity']
                total_cost += trans['quantity'] * trans['price']
            else:  # Sell
                total_shares_sold += trans['quantity']
                total_proceeds += trans['quantity'] * trans['price']
        
        # FIX: Use ACTUAL current shares from database, not calculated
        current_shares = stock['quantity']  # This ensures consistency
        average_buy_price = total_cost / total_shares_bought if total_shares_bought > 0 else 0
        current_value = current_shares * stock['price']
        unrealized_gain_loss = current_value - (current_shares * average_buy_price)
        
        return {
            'symbol': stock['symbol'],
            'current_shares': current_shares,  # Now shows correct actual quantity
            'current_price': stock['price'],
            'average_buy_price': average_buy_price,
            'total_invested': total_cost,
            'total_proceeds': total_proceeds,
            'current_value': current_value,
            'unrealized_gain_loss': unrealized_gain_loss,
            'unrealized_gain_loss_percent': (unrealized_gain_loss / (current_shares * average_buy_price)) * 100 if current_shares > 0 else 0,
            'transaction_count': len(transactions)
        }