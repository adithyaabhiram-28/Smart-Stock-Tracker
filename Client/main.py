import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Service.user_service import UserService
from Service.portfolio_service import PortfolioService
from Client.transaction_cli import TransactionCLI
from Client.stock_cli import StockCLI
from Client.portfolio_cli import PortfolioCLI
from Service.stock_service import StockService


class MainCLI:
    def __init__(self):
        self.user_service = UserService()
        self.portfolio_service = PortfolioService()
        self.current_user = None

    def menu(self):
        while True:
            print("\n" + "="*60)
            print("🚀 SMART STOCK TRACKER")
            print("="*60)
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            print("\n💡 Your all-in-one investment tracking solution")

            choice = input("\nEnter choice: ")
            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
            elif choice == "3":
                print("\nThank you for using Smart Stock Tracker! 📈")
                print("Goodbye! 👋")
                break
            else:
                print("❌ Invalid choice!")

    def register(self):
        print("\n--- User Registration ---")
        name = input("Enter your full name: ")
        email = input("Enter your email: ")
        try:
            self.user_service.register_user(name, email)
            print("✅ User registered successfully!")
            print(f"👋 Welcome to Smart Stock Tracker, {name}!")
        except ValueError as e:
            print(f"❌ Error: {e}")

    def login(self):
        print("\n--- User Login ---")
        email = input("Enter your email: ")
        user = self.user_service.user_dao.get_user_by_email(email)
        if user:
            self.current_user = user
            print(f"✅ Logged in successfully as {user['name']}!")
            self.dashboard()
        else:
            print("❌ User not found! Please check your email or register first.")

    def dashboard(self):
        """Main dashboard after login"""
        while True:
            # Check if user is still logged in
            if not self.current_user:
                break
            
            print("\n" + "="*60)
            print(f"🎯 INVESTMENT DASHBOARD - Welcome, {self.current_user['name']}!")
            print("="*60)
            print("1. Portfolio Management")
            print("2. Quick Portfolio Overview")
            print("3. Market Watch")
            print("4. Account Settings")
            print("5. Logout")
            print("\n💡 Track your investments in real-time!")

            choice = input("\nEnter choice: ")
            if choice == "1":
                PortfolioCLI(self.current_user).menu()
            elif choice == "2":
                self.quick_portfolio_overview()
            elif choice == "3":
                self.market_watch()
            elif choice == "4":
                self.account_settings()
                # Check if user was deleted during account settings
                if not self.current_user:
                    break
            elif choice == "5":
                print(f"👋 Goodbye, {self.current_user['name']}! Logging out...")
                self.current_user = None
                break
            else:
                print("❌ Invalid choice!")

    def quick_portfolio_overview(self):
        """Quick overview of all portfolios with total net worth"""
        print(f"\n📊 QUICK PORTFOLIO OVERVIEW")
        print("="*50)
        
        try:
            portfolio_summaries = self.portfolio_service.get_portfolio_summary(self.current_user["user_id"])
            
            if not portfolio_summaries:
                print("No portfolios found. Create your first portfolio to get started!")
                return
            
            total_net_worth = 0
            total_gain_loss = 0
            portfolio_count = len(portfolio_summaries)
            stock_count = 0
            
            print(f"\n🏠 Your Portfolios ({portfolio_count}):")
            print("─" * 60)
            
            for summary in portfolio_summaries:
                if 'error' not in summary:
                    total_net_worth += summary['current_value']
                    total_gain_loss += summary['total_gain_loss']
                    stock_count += summary['stock_count']
                    
                    gain_loss_icon = "🟢" if summary['total_gain_loss'] >= 0 else "🔴"
                    print(f"📁 {summary['portfolio_name']}")
                    print(f"   💰 Value: ${summary['current_value']:,.2f}")
                    print(f"   📈 P&L: {gain_loss_icon} ${summary['total_gain_loss']:,.2f} ({summary['gain_loss_percentage']:+.2f}%)")
                    print(f"   📊 Stocks: {summary['stock_count']}")
                    print()
                else:
                    print(f"📁 {summary['portfolio_name']} - ❌ Error: {summary['error']}")
                    print()
            
            # Overall summary
            print("─" * 60)
            overall_icon = "🟢" if total_gain_loss >= 0 else "🔴"
            print(f"💰 TOTAL NET WORTH: ${total_net_worth:,.2f}")
            print(f"📈 TOTAL GAIN/LOSS: {overall_icon} ${total_gain_loss:,.2f}")
            print(f"📊 PORTFOLIOS: {portfolio_count} | STOCKS: {stock_count}")
            
            # Quick actions
            print(f"\n⚡ Quick Actions:")
            print("1. Refresh All Portfolio Prices")
            print("2. View Detailed Analytics")
            print("3. Back to Dashboard")
            
            action = input("\nEnter choice: ")
            if action == "1":
                self.refresh_all_portfolios()
            elif action == "2":
                PortfolioCLI(self.current_user).menu()
                
        except Exception as e:
            print(f"❌ Error loading portfolio overview: {e}")

    def refresh_all_portfolios(self):
        """Refresh prices for all portfolios"""
        print(f"\n🔄 REFRESHING ALL PORTFOLIO PRICES")
        print("="*40)
        
        portfolios = self.portfolio_service.get_user_portfolios(self.current_user["user_id"])
        if not portfolios:
            print("No portfolios found.")
            return
        
        total_updated = 0
        for portfolio in portfolios:
            try:
                result = self.portfolio_service.refresh_portfolio_prices(portfolio['portfolio_id'])
                updated = result['stocks_updated']
                total_updated += updated
                print(f"✅ {portfolio['portfolio_name']}: Updated {updated} stocks")
            except Exception as e:
                print(f"❌ {portfolio['portfolio_name']}: Error - {e}")
        
        print(f"\n🎉 Successfully updated {total_updated} stock prices across {len(portfolios)} portfolios!")
        
        # Show updated overview
        input("\nPress Enter to view updated portfolio values...")
        self.quick_portfolio_overview()

    def market_watch(self):
        """Market watch feature to search and track stocks"""
        print(f"\n📈 MARKET WATCH")
        print("="*40)
        
        while True:
            print("\n1. Search Stock Information")
            print("2. View Market Trends (Top Stocks)")
            print("3. Back to Dashboard")
            
            choice = input("\nEnter choice: ")
            if choice == "1":
                self.search_stock_info()
            elif choice == "2":
                self.show_market_trends()
            elif choice == "3":
                break
            else:
                print("❌ Invalid choice!")

    def search_stock_info(self):
        """Search for stock information"""
        print(f"\n🔍 SEARCH STOCK INFORMATION")
        symbol = input("Enter stock symbol (e.g., AAPL, TSLA, GOOGL): ").strip().upper()
        
        if not symbol:
            return
        
        try:
            # Use StockService to get information
            stock_service = StockService()
            stock_info = stock_service.search_stock_info(symbol)
            
            print(f"\n📊 STOCK INFORMATION: {symbol}")
            print("="*50)
            print(f"🏢 Company: {stock_info['company_name']}")
            print(f"📛 Symbol: {stock_info['symbol']}")
            print(f"💰 Current Price: ${stock_info['current_price']:.2f}")
            print(f"📉 Previous Close: ${stock_info['previous_close']:.2f}")
            
            # Calculate and display price change
            if stock_info['previous_close'] > 0:
                change = stock_info['current_price'] - stock_info['previous_close']
                change_percent = (change / stock_info['previous_close']) * 100
                change_icon = "🟢" if change >= 0 else "🔴"
                print(f"📈 Daily Change: {change_icon} ${change:+.2f} ({change_percent:+.2f}%)")
            
            print(f"🏦 Market Cap: ${stock_info['market_cap']:,.0f}")
            print(f"📂 Sector: {stock_info['sector']}")
            print(f"🏭 Industry: {stock_info['industry']}")
            print(f"📝 About: {stock_info['description']}")
            
            # Quick action to add to portfolio
            print(f"\n💼 Quick Action:")
            add_to_portfolio = input(f"Add {symbol} to a portfolio? (y/n): ")
            if add_to_portfolio.lower() == 'y':
                self.add_stock_to_portfolio(symbol, stock_info['current_price'])
                
        except ValueError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    def add_stock_to_portfolio(self, symbol, current_price):
        """Quick add stock to portfolio"""
        portfolios = self.portfolio_service.get_user_portfolios(self.current_user["user_id"])
        if not portfolios:
            print("❌ No portfolios found. Please create a portfolio first.")
            return
        
        print(f"\n📁 Available Portfolios:")
        for i, portfolio in enumerate(portfolios, 1):
            print(f"{i}. {portfolio['portfolio_name']}")
        
        try:
            choice = int(input(f"\nSelect portfolio (1-{len(portfolios)}): ")) - 1
            if 0 <= choice < len(portfolios):
                selected_portfolio = portfolios[choice]
                quantity = int(input(f"Enter quantity of {symbol} to add: "))
                
                stock_service = StockService()
                stock_service.add_stock(selected_portfolio['portfolio_id'], symbol, quantity, current_price)
                
                total_cost = current_price * quantity
                print(f"✅ Successfully added {quantity} shares of {symbol} to {selected_portfolio['portfolio_name']}!")
                print(f"💰 Total Cost: ${total_cost:,.2f}")
            else:
                print("❌ Invalid selection!")
        except (ValueError, IndexError):
            print("❌ Invalid input!")

    def show_market_trends(self):
        """Show popular market stocks"""
        print(f"\n📈 MARKET TRENDS - POPULAR STOCKS")
        print("="*50)
        
        popular_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
            "META", "NVDA", "NFLX", "AMD", "INTC"
        ]
        
        stock_service = StockService()
        
        print(f"\n🔍 Fetching latest prices...")
        print(f"{'Symbol':<8} {'Company':<20} {'Price':<12} {'Change':<15}")
        print("─" * 55)
        
        for symbol in popular_stocks:
            try:
                stock_info = stock_service.search_stock_info(symbol)
                change = stock_info['current_price'] - stock_info['previous_close']
                change_percent = (change / stock_info['previous_close']) * 100
                change_icon = "🟢" if change >= 0 else "🔴"
                change_str = f"{change_icon} ${change:+.2f} ({change_percent:+.1f}%)"
                
                # Truncate company name
                company_name = stock_info['company_name'][:18] + "..." if len(stock_info['company_name']) > 18 else stock_info['company_name']
                
                print(f"{symbol:<8} {company_name:<20} ${stock_info['current_price']:<11.2f} {change_str:<15}")
                
            except Exception as e:
                print(f"{symbol:<8} {'Error fetching data':<20} {'N/A':<12} {'N/A':<15}")
        
        print(f"\n💡 Tip: Use 'Search Stock Information' for detailed analysis")

    def account_settings(self):
        """User account settings"""
        print(f"\n⚙️  ACCOUNT SETTINGS")
        print("="*40)
        
        while True:
            print(f"\n👤 User: {self.current_user['name']}")
            print(f"📧 Email: {self.current_user['email']}")
            print(f"🆔 User ID: {self.current_user['user_id']}")
            
            print(f"\n1. Update Profile")
            print("2. Delete Account")
            print("3. Back to Dashboard")
            
            choice = input("\nEnter choice: ")
            if choice == "1":
                self.update_profile()
            elif choice == "2":
                self.delete_account()
                break  # Return to main menu if account deleted
            elif choice == "3":
                break
            else:
                print("❌ Invalid choice!")

    def update_profile(self):
        """Update user profile"""
        print(f"\n✏️  UPDATE PROFILE")
        new_name = input(f"Enter new name (current: {self.current_user['name']}): ").strip()
        new_email = input(f"Enter new email (current: {self.current_user['email']}): ").strip()
        
        if not new_name and not new_email:
            print("ℹ️ No changes made.")
            return
        
        if not new_name:
            new_name = self.current_user['name']
        if not new_email:
            new_email = self.current_user['email']
        
        confirm = input(f"\nUpdate profile to:\nName: {new_name}\nEmail: {new_email}\nConfirm? (y/n): ")
        if confirm.lower() == 'y':
            try:
                self.user_service.update_profile(self.current_user["user_id"], new_name, new_email)
                # Update current user data
                self.current_user['name'] = new_name
                self.current_user['email'] = new_email
                print("✅ Profile updated successfully!")
            except ValueError as e:
                print(f"❌ Error: {e}")

    def delete_account(self):
        """Delete user account"""
        print(f"\n🗑️  DELETE ACCOUNT")
        print("❌ WARNING: This action cannot be undone!")
        print("❌ All your portfolios, stocks, and transactions will be permanently deleted!")
        
        confirm1 = input(f"\nAre you sure you want to delete your account? (type 'DELETE' to confirm): ")
        if confirm1 != "DELETE":
            print("ℹ️ Account deletion cancelled.")
            return
        
        confirm2 = input(f"FINAL WARNING: This will erase ALL your data permanently! (type 'CONFIRM' to proceed): ")
        if confirm2 == "CONFIRM":
            try:
                self.user_service.delete_account(self.current_user["user_id"])
                print("✅ Account deleted successfully!")
                self.current_user = None
                return True  # Indicate that account was deleted
            except ValueError as e:
                print(f"❌ Error: {e}")
        else:
            print("ℹ️ Account deletion cancelled.")
        return False


if __name__ == "__main__":
    # Check for required dependencies
    try:
        import yfinance
        print("🚀 Starting Smart Stock Tracker...")
        MainCLI().menu()
    except ImportError:
        print("❌ Missing required dependencies!")
        print("💡 Please install required packages: pip install yfinance pandas")
        print("💡 Or run: pip install -r requirements.txt")