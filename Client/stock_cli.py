import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Service.stock_service import StockService

class StockCLI:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.service = StockService()

    def menu(self):
        while True:
            print(f"\n" + "="*60)
            print(f"📈 STOCK MANAGEMENT - {self.portfolio['portfolio_name']}")
            print("="*60)
            print("1. Add Stock (with Live Price)")
            print("2. Add Stock (Manual Price)")
            print("3. Search Stock Information")
            print("4. View Stocks & Portfolio Value")
            print("5. Update Stock")
            print("6. Delete Stock")
            print("7. Refresh Stock Prices")
            print("8. Refresh Single Stock Price")
            print("9. Back to Portfolio Menu")
            choice = input("\nEnter choice: ")

            if choice == "1":
                self.add_stock_with_live_price()
            elif choice == "2":
                self.add_stock_manual_price()
            elif choice == "3":
                self.search_stock_info()
            elif choice == "4":
                self.view_stocks()
            elif choice == "5":
                self.update_stock()
            elif choice == "6":
                self.delete_stock()
            elif choice == "7":
                self.refresh_all_prices()
            elif choice == "8":
                self.refresh_single_price()
            elif choice == "9":
                break
            else:
                print("❌ Invalid choice!")

    def add_stock_with_live_price(self):
        print(f"\n--- Add Stock with Live Price ---")
        symbol = input("Enter stock symbol (e.g., AAPL, TSLA, GOOGL): ").strip().upper()
        quantity = self.get_positive_integer("Enter quantity: ")
        
        try:
            # First, show the user what they're buying
            stock_info = self.service.search_stock_info(symbol)
            print(f"\n📋 Stock Information:")
            print(f"   Company: {stock_info['company_name']}")
            print(f"   Symbol: {stock_info['symbol']}")
            print(f"   Current Price: ${stock_info['current_price']:.2f}")
            print(f"   Previous Close: ${stock_info['previous_close']:.2f}")
            print(f"   Sector: {stock_info['sector']}")
            
            confirm = input(f"\nAdd {quantity} shares of {symbol} at ${stock_info['current_price']:.2f}? (y/n): ")
            if confirm.lower() == 'y':
                self.service.add_stock_with_live_price(self.portfolio["portfolio_id"], symbol, quantity)
                total_cost = stock_info['current_price'] * quantity
                print(f"✅ Successfully added {quantity} shares of {symbol} at ${stock_info['current_price']:.2f}")
                print(f"💰 Total Cost: ${total_cost:,.2f}")
        except ValueError as e:
            print(f"❌ Error: {e}")

    def add_stock_manual_price(self):
        print(f"\n--- Add Stock with Manual Price ---")
        symbol = input("Enter stock symbol: ").strip().upper()
        price = self.get_positive_float("Enter stock price: $")
        quantity = self.get_positive_integer("Enter quantity: ")
        
        try:
            total_cost = price * quantity
            confirm = input(f"\nAdd {quantity} shares of {symbol} at ${price:.2f}? Total: ${total_cost:,.2f} (y/n): ")
            if confirm.lower() == 'y':
                self.service.add_stock(self.portfolio["portfolio_id"], symbol, price, quantity)
                print(f"✅ Stock added successfully!")
                print(f"📦 {quantity} shares of {symbol} at ${price:.2f} = ${total_cost:,.2f}")
        except ValueError as e:
            print(f"❌ Error: {e}")

    def search_stock_info(self):
        print(f"\n--- Search Stock Information ---")
        symbol = input("Enter stock symbol to search: ").strip().upper()
        
        try:
            stock_info = self.service.search_stock_info(symbol)
            print(f"\n📊 STOCK INFORMATION: {symbol}")
            print("─" * 50)
            print(f"🏢 Company: {stock_info['company_name']}")
            print(f"📛 Symbol: {stock_info['symbol']}")
            print(f"💰 Current Price: ${stock_info['current_price']:.2f}")
            print(f"📉 Previous Close: ${stock_info['previous_close']:.2f}")
            print(f"🏦 Market Cap: ${stock_info['market_cap']:,.0f}")
            print(f"📂 Sector: {stock_info['sector']}")
            print(f"🏭 Industry: {stock_info['industry']}")
            print(f"📝 Description: {stock_info['description']}")
            
            # Show price change
            if stock_info['previous_close'] > 0:
                change = stock_info['current_price'] - stock_info['previous_close']
                change_percent = (change / stock_info['previous_close']) * 100
                change_icon = "🟢" if change >= 0 else "🔴"
                print(f"📈 Daily Change: {change_icon} ${change:+.2f} ({change_percent:+.2f}%)")
                
        except ValueError as e:
            print(f"❌ Error: {e}")

    def view_stocks(self):
        print(f"\n--- Stocks in {self.portfolio['portfolio_name']} ---")
        stocks = self.service.get_stocks(self.portfolio["portfolio_id"])
        
        if stocks:
            total_portfolio_value = 0
            print(f"\n{'Symbol':<8} {'Quantity':<10} {'Price':<12} {'Total Value':<15}")
            print("─" * 50)
            
            for stock in stocks:
                total_value = stock['price'] * stock['quantity']
                total_portfolio_value += total_value
                print(f"{stock['symbol']:<8} {stock['quantity']:<10} ${stock['price']:<11.2f} ${total_value:<14,.2f}")
            
            print("─" * 50)
            print(f"💰 TOTAL PORTFOLIO VALUE: ${total_portfolio_value:,.2f}")
            
            # Show stock count and last updated
            print(f"📊 Stocks: {len(stocks)} | Last Updated: {stocks[0].get('created_at', 'N/A')}")
        else:
            print("No stocks found in this portfolio.")

    def update_stock(self):
        print(f"\n--- Update Stock ---")
        self.view_stocks()
        
        sid = input("\nEnter stock ID to update: ").strip()
        if not sid:
            return
            
        # Show current stock details
        try:
            stock_data = self.service.stock_dao.get_stock_by_id(sid)
            if not stock_data:
                print("❌ Stock not found!")
                return
                
            stock = stock_data[0]
            print(f"\nCurrent: {stock['symbol']} - Qty: {stock['quantity']} - Price: ${stock['price']:.2f}")
            
            # Get updates
            price_input = input("Enter new price (or press Enter to keep current): ").strip()
            qty_input = input("Enter new quantity (or press Enter to keep current): ").strip()
            
            price = float(price_input) if price_input else None
            quantity = int(qty_input) if qty_input else None
            
            if price is None and quantity is None:
                print("ℹ️ No changes made.")
                return
                
            self.service.update_stock(sid, price, quantity)
            print("✅ Stock updated successfully!")
            
        except ValueError as e:
            print(f"❌ Error: {e}")

    def delete_stock(self):
        print(f"\n--- Delete Stock ---")
        self.view_stocks()
        
        sid = input("\nEnter stock ID to delete: ").strip()
        if not sid:
            return
            
        # Show what we're deleting
        try:
            stock_data = self.service.stock_dao.get_stock_by_id(sid)
            if not stock_data:
                print("❌ Stock not found!")
                return
                
            stock = stock_data[0]
            total_value = stock['price'] * stock['quantity']
            
            confirm = input(f"❓ Delete {stock['quantity']} shares of {stock['symbol']} (worth ${total_value:,.2f})? (y/n): ")
            if confirm.lower() == 'y':
                self.service.delete_stock(sid)
                print("✅ Stock deleted successfully!")
                
        except ValueError as e:
            print(f"❌ Error: {e}")

    def refresh_all_prices(self):
        print(f"\n--- Refresh All Stock Prices ---")
        stocks = self.service.get_stocks(self.portfolio["portfolio_id"])
        
        if not stocks:
            print("No stocks to refresh.")
            return
            
        print(f"🔄 Refreshing prices for {len(stocks)} stocks...")
        
        try:
            updated_count = self.service.refresh_stock_prices(self.portfolio["portfolio_id"])
            print(f"✅ Successfully updated {updated_count} stock prices")
            
            # Show updated portfolio
            self.view_stocks()
            
        except Exception as e:
            print(f"❌ Error refreshing prices: {e}")

    def refresh_single_price(self):
        print(f"\n--- Refresh Single Stock Price ---")
        self.view_stocks()
        
        sid = input("\nEnter stock ID to refresh price: ").strip()
        if not sid:
            return
            
        try:
            new_price = self.service.refresh_single_stock_price(sid)
            stock_data = self.service.stock_dao.get_stock_by_id(sid)
            if stock_data:
                stock = stock_data[0]
                print(f"✅ {stock['symbol']} price updated to ${new_price:.2f}")
                
        except ValueError as e:
            print(f"❌ Error: {e}")

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