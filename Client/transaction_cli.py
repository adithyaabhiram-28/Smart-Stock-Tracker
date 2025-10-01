import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Service.transaction_service import TransactionService
from Service.stock_service import StockService
from datetime import datetime

class TransactionCLI:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.trans_service = TransactionService()
        self.stock_service = StockService()

    def menu(self):
        while True:
            print(f"\n" + "="*60)
            print(f"💰 TRANSACTION MANAGEMENT - {self.portfolio['portfolio_name']}")
            print("="*60)
            print("1. Buy Stock")
            print("2. Sell Stock")
            print("3. View All Transactions")
            print("4. Portfolio Performance Analytics")
            print("5. Transaction Analytics & Trends")
            print("6. Stock Performance Analysis")
            print("7. Back to Portfolio Menu")
            choice = input("\nEnter choice: ")

            if choice == "1":
                self.buy_stock()
            elif choice == "2":
                self.sell_stock()
            elif choice == "3":
                self.view_transactions()
            elif choice == "4":
                self.portfolio_performance()
            elif choice == "5":
                self.transaction_analytics()
            elif choice == "6":
                self.stock_performance_analysis()
            elif choice == "7":
                break
            else:
                print("❌ Invalid choice!")

    def buy_stock(self):
        print(f"\n--- Buy Stock ---")
        self.show_stocks_with_prices()
        
        stock_id = input("\nEnter stock ID to buy: ").strip()
        if not stock_id:
            return
            
        # Get stock info for confirmation
        stock_data = self.stock_service.stock_dao.get_stock_by_id(stock_id)
        if not stock_data:
            print("❌ Stock not found!")
            return
            
        stock = stock_data[0]
        current_price = stock['price']
        
        print(f"\n💡 Buying {stock['symbol']} - Current Price: ${current_price:.2f}")
        
        quantity = self.get_positive_integer("Enter quantity to buy: ")
        price = self.get_positive_float(f"Enter price per stock (Current: ${current_price:.2f}): $")
        
        total_cost = quantity * price
        confirm = input(f"\nConfirm buy {quantity} shares of {stock['symbol']} at ${price:.2f}? Total: ${total_cost:,.2f} (y/n): ")
        
        if confirm.lower() == 'y':
            try:
                self.trans_service.buy_stock(self.portfolio['portfolio_id'], stock_id, quantity, price)
                print(f"✅ Successfully purchased {quantity} shares of {stock['symbol']}!")
                print(f"💰 Total Cost: ${total_cost:,.2f}")
            except ValueError as e:
                print(f"❌ Error: {e}")

    def sell_stock(self):
        print(f"\n--- Sell Stock ---")
        self.show_stocks_with_prices()
        
        stock_id = input("\nEnter stock ID to sell: ").strip()
        if not stock_id:
            return
            
        # Get stock info for confirmation
        stock_data = self.stock_service.stock_dao.get_stock_by_id(stock_id)
        if not stock_data:
            print("❌ Stock not found!")
            return
            
        stock = stock_data[0]
        current_price = stock['price']
        available_quantity = stock['quantity']
        
        print(f"\n💡 Selling {stock['symbol']} - Available: {available_quantity} shares - Current Price: ${current_price:.2f}")
        
        quantity = self.get_positive_integer("Enter quantity to sell: ")
        if quantity > available_quantity:
            print(f"❌ Cannot sell {quantity} shares, only {available_quantity} available!")
            return
            
        price = self.get_positive_float(f"Enter price per stock (Current: ${current_price:.2f}): $")
        
        total_proceeds = quantity * price
        confirm = input(f"\nConfirm sell {quantity} shares of {stock['symbol']} at ${price:.2f}? Total: ${total_proceeds:,.2f} (y/n): ")
        
        if confirm.lower() == 'y':
            try:
                self.trans_service.sell_stock(self.portfolio['portfolio_id'], stock_id, quantity, price)
                print(f"✅ Successfully sold {quantity} shares of {stock['symbol']}!")
                print(f"💰 Total Proceeds: ${total_proceeds:,.2f}")
                
                # Show remaining quantity
                if quantity < available_quantity:
                    remaining = available_quantity - quantity
                    print(f"📦 Remaining shares: {remaining}")
                    
            except ValueError as e:
                print(f"❌ Error: {e}")

    def view_transactions(self):
        print(f"\n--- All Transactions for {self.portfolio['portfolio_name']} ---")
        transactions = self.trans_service.get_portfolio_transactions(self.portfolio['portfolio_id'])
        
        if transactions:
            total_buys = 0
            total_sells = 0
            
            print(f"\n{'Date':<12} {'Type':<6} {'Symbol':<8} {'Quantity':<10} {'Price':<12} {'Total':<15}")
            print("─" * 70)
            
            for t in transactions:
                # Get stock symbol
                stock_data = self.stock_service.stock_dao.get_stock_by_id(t['stock_id'])
                symbol = stock_data[0]['symbol'] if stock_data else f"ID:{t['stock_id']}"
                
                # Format date
                trans_date = t.get('date', '')
                if trans_date:
                    if isinstance(trans_date, str) and 'T' in trans_date:
                        trans_date = trans_date.split('T')[0]
                
                quantity = t['quantity']
                price = t['price']
                total = quantity * price
                trans_type = t['type']
                
                # Color code buys/sells
                type_icon = "🟢 BUY" if trans_type == 'Buy' else "🔴 SELL"
                
                print(f"{trans_date:<12} {type_icon:<6} {symbol:<8} {quantity:<10} ${price:<11.2f} ${total:<14,.2f}")
                
                if trans_type == 'Buy':
                    total_buys += total
                else:
                    total_sells += total
            
            print("─" * 70)
            print(f"📊 Total Buys: ${total_buys:,.2f} | Total Sells: ${total_sells:,.2f}")
            print(f"📈 Net Cash Flow: ${total_sells - total_buys:,.2f}")
            print(f"🔢 Total Transactions: {len(transactions)}")
            
        else:
            print("No transactions found for this portfolio.")

    def portfolio_performance(self):
        print(f"\n--- Portfolio Performance Analytics ---")
        try:
            performance = self.trans_service.get_portfolio_performance(self.portfolio['portfolio_id'])
            
            print(f"\n📊 PERFORMANCE SUMMARY: {self.portfolio['portfolio_name']}")
            print("="*50)
            
            # Basic metrics
            print(f"💰 Total Invested: ${performance['total_invested']:,.2f}")
            print(f"📈 Current Holdings Value: ${performance['current_holdings_value']:,.2f}")
            print(f"💵 Total Sales: ${performance['total_sold']:,.2f}")
            print(f"🏦 Net Portfolio Value: ${performance['net_value']:,.2f}")
            
            # Gain/Loss with color coding
            gain_loss = performance['total_gain_loss']
            gain_icon = "🟢" if gain_loss >= 0 else "🔴"
            print(f"🎯 Total Gain/Loss: {gain_icon} ${gain_loss:,.2f}")
            print(f"📊 Return: {gain_icon} {performance['gain_loss_percentage']:+.2f}%")
            
            # Activity metrics
            print(f"\n📈 ACTIVITY METRICS:")
            print(f"   Total Transactions: {performance['transaction_count']}")
            print(f"   Buy Volume: ${performance['buy_volume']:,.2f}")
            print(f"   Sell Volume: ${performance['sell_volume']:,.2f}")
            print(f"   Recent Activity (30 days): {performance['recent_activity']} transactions")
            print(f"   Stocks Currently Held: {performance['stocks_held']}")
            
        except Exception as e:
            print(f"❌ Error generating performance analytics: {e}")

    def transaction_analytics(self):
        print(f"\n--- Transaction Analytics & Trends ---")
        try:
            analytics = self.trans_service.get_transaction_analytics(self.portfolio['portfolio_id'])
            
            if 'error' in analytics:
                print(f"❌ {analytics['error']}")
                return
            
            print(f"\n📈 TRANSACTION ANALYTICS: {self.portfolio['portfolio_name']}")
            print("="*50)
            
            # Monthly breakdown
            monthly_data = analytics.get('monthly_breakdown', {})
            if monthly_data:
                print(f"\n📅 MONTHLY TRADING ACTIVITY:")
                print(f"{'Month':<10} {'Buys':<6} {'Sells':<6} {'Buy Vol':<12} {'Sell Vol':<12}")
                print("─" * 50)
                
                for month, data in sorted(monthly_data.items(), reverse=True):
                    print(f"{month:<10} {data['buys']:<6} {data['sells']:<6} ${data['buy_volume']:<11,.0f} ${data['sell_volume']:<11,.0f}")
            
            # Most traded stocks
            most_traded = analytics.get('most_traded_stocks', [])
            if most_traded:
                print(f"\n🏆 MOST TRADED STOCKS:")
                print(f"{'Symbol':<8} {'Buys':<6} {'Sells':<6} {'Total Volume':<15}")
                print("─" * 40)
                
                for stock in most_traded:
                    print(f"{stock['symbol']:<8} {stock['buys']:<6} {stock['sells']:<6} ${stock['volume']:<14,.0f}")
            
            # Buy/Sell ratio
            ratio = analytics.get('buy_sell_ratio', {})
            if ratio:
                print(f"\n⚖️  TRADING BEHAVIOR:")
                print(f"   Buy Ratio: {ratio['buy_ratio']:.1f}%")
                print(f"   Sell Ratio: {ratio['sell_ratio']:.1f}%")
                
                if ratio['buy_ratio'] > 60:
                    print("   📈 Trend: Accumulation Phase")
                elif ratio['sell_ratio'] > 60:
                    print("   📉 Trend: Profit Taking Phase")
                else:
                    print("   ⚖️  Trend: Balanced Trading")
            
            print(f"\n🔢 Total Transactions: {analytics['total_transactions']}")
            
        except Exception as e:
            print(f"❌ Error generating transaction analytics: {e}")

    def stock_performance_analysis(self):
        print(f"\n--- Stock Performance Analysis ---")
        self.show_stocks_with_prices()
        
        stock_id = input("\nEnter stock ID for performance analysis (or press Enter for all stocks): ").strip()
        
        if stock_id:
            # Single stock analysis
            try:
                performance = self.trans_service.get_stock_performance(stock_id)
                
                if 'error' in performance:
                    print(f"❌ {performance['error']}")
                    return
                
                stock_data = self.stock_service.stock_dao.get_stock_by_id(stock_id)
                if stock_data:
                    stock = stock_data[0]
                    
                    print(f"\n📊 PERFORMANCE ANALYSIS: {performance['symbol']}")
                    print("="*50)
                    print(f"🏢 Current Shares: {performance['current_shares']}")
                    print(f"💰 Current Price: ${performance['current_price']:.2f}")
                    print(f"📊 Average Buy Price: ${performance['average_buy_price']:.2f}")
                    print(f"💵 Total Invested: ${performance['total_invested']:,.2f}")
                    print(f"💰 Total Proceeds: ${performance['total_proceeds']:,.2f}")
                    print(f"📈 Current Value: ${performance['current_value']:,.2f}")
                    
                    # Unrealized gain/loss
                    unrealized = performance['unrealized_gain_loss']
                    unrealized_icon = "🟢" if unrealized >= 0 else "🔴"
                    print(f"🎯 Unrealized Gain/Loss: {unrealized_icon} ${unrealized:,.2f}")
                    print(f"📊 Unrealized Return: {unrealized_icon} {performance['unrealized_gain_loss_percent']:+.2f}%")
                    
                    print(f"🔢 Transaction Count: {performance['transaction_count']}")
                    
            except Exception as e:
                print(f"❌ Error analyzing stock performance: {e}")
        else:
            # All stocks analysis
            stocks = self.stock_service.get_stocks(self.portfolio['portfolio_id'])
            if not stocks:
                print("No stocks found in portfolio.")
                return
                
            print(f"\n📊 PERFORMANCE SUMMARY - ALL STOCKS")
            print("="*60)
            print(f"{'Symbol':<8} {'Shares':<8} {'Cur Price':<12} {'Avg Cost':<12} {'Cur Value':<12} {'Gain/Loss':<12}")
            print("─" * 70)
            
            total_unrealized = 0
            for stock in stocks:
                try:
                    performance = self.trans_service.get_stock_performance(stock['stock_id'])
                    if 'error' not in performance:
                        unrealized = performance['unrealized_gain_loss']
                        total_unrealized += unrealized
                        unrealized_icon = "🟢" if unrealized >= 0 else "🔴"
                        
                        print(f"{stock['symbol']:<8} {performance['current_shares']:<8} ${stock['price']:<11.2f} ${performance['average_buy_price']:<11.2f} ${performance['current_value']:<11.2f} {unrealized_icon} ${unrealized:<10.2f}")
                except:
                    continue
            
            print("─" * 70)
            total_icon = "🟢" if total_unrealized >= 0 else "🔴"
            print(f"TOTAL UNREALIZED GAIN/LOSS: {total_icon} ${total_unrealized:,.2f}")

    def show_stocks_with_prices(self):
        """Enhanced helper to display current stocks with live prices"""
        stocks = self.stock_service.get_stocks(self.portfolio['portfolio_id'])
        if stocks:
            total_value = 0
            print(f"\n📦 CURRENT STOCKS IN PORTFOLIO:")
            print(f"{'ID':<10} {'Symbol':<8} {'Quantity':<10} {'Price':<12} {'Total Value':<15}")
            print("─" * 65)
            
            for stock in stocks:
                stock_value = stock['price'] * stock['quantity']
                total_value += stock_value
                print(f"{stock['stock_id']:<10} {stock['symbol']:<8} {stock['quantity']:<10} ${stock['price']:<11.2f} ${stock_value:<14,.2f}")
            
            print("─" * 65)
            print(f"💰 TOTAL PORTFOLIO VALUE: ${total_value:,.2f}")
        else:
            print("No stocks in portfolio yet.")

    def get_positive_integer(self, prompt):
        """Helper to get positive integer input"""
        while True:
            try:
                value = int(input(prompt))
                if value <= 0:
                    print("❌ Please enter a positive number")
                    continue
                return value
            except ValueError:
                print("❌ Please enter a valid number")

    def get_positive_float(self, prompt):
        """Helper to get positive float input"""
        while True:
            try:
                value = float(input(prompt))
                if value <= 0:
                    print("❌ Please enter a positive number")
                    continue
                return value
            except ValueError:
                print("❌ Please enter a valid number")