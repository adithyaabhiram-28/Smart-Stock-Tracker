import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Service.portfolio_service import PortfolioService
from Client.stock_cli import StockCLI
from Client.transaction_cli import TransactionCLI

class PortfolioCLI:
    def __init__(self, user):
        self.user = user
        self.service = PortfolioService()

    def menu(self):
        while True:
            print("\n" + "="*50)
            print("📊 PORTFOLIO MANAGEMENT")
            print("="*50)
            print("1. Create Portfolio")
            print("2. View My Portfolios")
            print("3. Portfolio Analytics")
            print("4. Refresh Portfolio Prices")
            print("5. Update Portfolio Name")
            print("6. Delete Portfolio")
            print("7. Back to Main Menu")
            choice = input("\nEnter choice: ")

            if choice == "1":
                self.create_portfolio()
            elif choice == "2":
                self.view_portfolios()
            elif choice == "3":
                self.portfolio_analytics()
            elif choice == "4":
                self.refresh_portfolio_prices()
            elif choice == "5":
                self.update_portfolio()
            elif choice == "6":
                self.delete_portfolio()
            elif choice == "7":
                break
            else:
                print("❌ Invalid choice!")

    def create_portfolio(self):
        print("\n--- Create New Portfolio ---")
        name = input("Enter portfolio name: ")
        try:
            self.service.create_portfolio(self.user['user_id'], name)
            print("✅ Portfolio created successfully!")
        except ValueError as e:
            print("❌ Error:", e)

    def view_portfolios(self):
        print("\n--- Your Portfolios ---")
        portfolio_summaries = self.service.get_portfolio_summary(self.user['user_id'])
        
        if portfolio_summaries:
            total_net_worth = 0
            total_gain_loss = 0
            
            for summary in portfolio_summaries:
                if 'error' not in summary:
                    total_net_worth += summary['current_value']
                    total_gain_loss += summary['total_gain_loss']
                    
                    gain_loss_color = "🟢" if summary['total_gain_loss'] >= 0 else "🔴"
                    print(f"\n📁 {summary['portfolio_name']} (ID: {summary['portfolio_id']})")
                    print(f"   💰 Current Value: ${summary['current_value']:,.2f}")
                    print(f"   📈 Gain/Loss: {gain_loss_color} ${summary['total_gain_loss']:,.2f} ({summary['gain_loss_percentage']:+.2f}%)")
                    print(f"   📊 Stocks: {summary['stock_count']}")
                else:
                    print(f"\n📁 {summary['portfolio_name']} (ID: {summary['portfolio_id']})")
                    print(f"   ❌ Error loading analytics: {summary['error']}")
            
            # Display totals
            print("\n" + "─" * 40)
            total_color = "🟢" if total_gain_loss >= 0 else "🔴"
            print(f"💰 TOTAL NET WORTH: ${total_net_worth:,.2f}")
            print(f"📈 TOTAL GAIN/LOSS: {total_color} ${total_gain_loss:,.2f}")
            
            # Option to manage specific portfolio
            self.manage_specific_portfolio()
        else:
            print("No portfolios found. Create your first portfolio!")

    def portfolio_analytics(self):
        print("\n--- Portfolio Analytics ---")
        portfolios = self.service.get_user_portfolios(self.user['user_id'])
        
        if not portfolios:
            print("No portfolios found.")
            return
        
        # List portfolios
        for p in portfolios:
            print(f"ID: {p['portfolio_id']} | Name: {p['portfolio_name']}")
        
        pid = input("\nEnter portfolio ID for detailed analytics (or press Enter to go back): ")
        if pid:
            try:
                analytics = self.service.get_portfolio_analytics(pid)
                self.display_detailed_analytics(analytics)
            except ValueError as e:
                print(f"❌ Error: {e}")

    def display_detailed_analytics(self, analytics):
        """Display comprehensive portfolio analytics"""
        portfolio = analytics['portfolio_info']
        performance = analytics['performance']
        stocks = analytics['stocks']
        
        print(f"\n" + "="*60)
        print(f"📊 DETAILED ANALYTICS: {portfolio['portfolio_name']}")
        print("="*60)
        
        # Performance metrics
        print(f"\n💰 FINANCIAL OVERVIEW:")
        print(f"   Total Invested: ${performance['total_invested']:,.2f}")
        print(f"   Current Value: ${performance['current_value']:,.2f}")
        print(f"   Total Sales: ${performance['total_sold']:,.2f}")
        print(f"   Net Portfolio Value: ${performance['net_value']:,.2f}")
        
        gain_loss_color = "🟢" if performance['total_gain_loss'] >= 0 else "🔴"
        print(f"   Total Gain/Loss: {gain_loss_color} ${performance['total_gain_loss']:,.2f}")
        print(f"   Return: {gain_loss_color} {performance['gain_loss_percentage']:+.2f}%")
        
        # Stock holdings
        print(f"\n📈 STOCK HOLDINGS ({len(stocks)} stocks):")
        if stocks:
            for stock in stocks:
                value = stock['price'] * stock['quantity']
                print(f"   {stock['symbol']}: {stock['quantity']} shares @ ${stock['price']:.2f} = ${value:,.2f}")
            
            # Top performers
            if analytics['top_stock']:
                top = analytics['top_stock']
                top_value = top['price'] * top['quantity']
                print(f"\n⭐ TOP HOLDING: {top['symbol']} (${top_value:,.2f})")
            
            if analytics['highest_quantity_stock']:
                high_qty = analytics['highest_quantity_stock']
                print(f"📦 LARGEST POSITION: {high_qty['symbol']} ({high_qty['quantity']} shares)")
        else:
            print("   No stocks in this portfolio.")

    def refresh_portfolio_prices(self):
        print("\n--- Refresh Portfolio Prices ---")
        portfolios = self.service.get_user_portfolios(self.user['user_id'])
        
        if not portfolios:
            print("No portfolios found.")
            return
        
        for p in portfolios:
            print(f"ID: {p['portfolio_id']} | Name: {p['portfolio_name']}")
        
        pid = input("\nEnter portfolio ID to refresh prices (or press Enter to go back): ")
        if pid:
            try:
                result = self.service.refresh_portfolio_prices(pid)
                print(f"✅ Successfully updated {result['stocks_updated']} stocks in '{result['portfolio_name']}'")
            except ValueError as e:
                print(f"❌ Error: {e}")

    def update_portfolio(self):
        print("\n--- Update Portfolio ---")
        portfolios = self.service.get_user_portfolios(self.user['user_id'])
        
        if not portfolios:
            print("No portfolios found.")
            return
        
        for p in portfolios:
            print(f"ID: {p['portfolio_id']} | Name: {p['portfolio_name']}")
        
        pid = input("\nEnter portfolio ID to update: ")
        new_name = input("Enter new portfolio name: ")
        
        try:
            self.service.update_portfolio(pid, new_name)
            print("✅ Portfolio updated successfully!")
        except ValueError as e:
            print(f"❌ Error: {e}")

    def delete_portfolio(self):
        print("\n--- Delete Portfolio ---")
        portfolios = self.service.get_user_portfolios(self.user['user_id'])
        
        if not portfolios:
            print("No portfolios found.")
            return
        
        for p in portfolios:
            print(f"ID: {p['portfolio_id']} | Name: {p['portfolio_name']}")
        
        pid = input("\nEnter portfolio ID to delete: ")
        confirm = input("❓ Are you sure? This will delete ALL stocks and transactions in this portfolio! (y/n): ")
        
        if confirm.lower() == "y":
            try:
                self.service.delete_portfolio(pid)
                print("✅ Portfolio deleted successfully!")
            except ValueError as e:
                print(f"❌ Error: {e}")

    def manage_specific_portfolio(self):
        """Allow user to select a specific portfolio for detailed management"""
        pid = input("\nEnter portfolio ID to manage stocks/transactions (or press Enter to go back): ")
        if pid:
            try:
                portfolio = self.service.portfolio_dao.get_portfolio_by_id(pid)
                if portfolio:
                    self.portfolio_management_menu(portfolio)
                else:
                    print("❌ Invalid portfolio ID")
            except Exception as e:
                print(f"❌ Error: {e}")

    def portfolio_management_menu(self, portfolio):
        """Menu for managing a specific portfolio's stocks and transactions"""
        while True:
            print(f"\n" + "="*50)
            print(f"🎯 MANAGING PORTFOLIO: {portfolio['portfolio_name']}")
            print("="*50)
            print("1. Manage Stocks")
            print("2. Manage Transactions")
            print("3. View Portfolio Analytics")
            print("4. Refresh Stock Prices")
            print("5. Back to Portfolio Menu")
            
            choice = input("\nEnter choice: ")
            if choice == "1":
                StockCLI(portfolio).menu()
            elif choice == "2":
                TransactionCLI(portfolio).menu()
            elif choice == "3":
                analytics = self.service.get_portfolio_analytics(portfolio['portfolio_id'])
                self.display_detailed_analytics(analytics)
            elif choice == "4":
                result = self.service.refresh_portfolio_prices(portfolio['portfolio_id'])
                print(f"✅ Updated {result['stocks_updated']} stock prices")
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice!")