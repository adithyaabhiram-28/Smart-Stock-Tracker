import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import(module_path, import_statement):
    try:
        exec(import_statement)
        print(f"✅ {module_path}: SUCCESS")
        return True
    except ImportError as e:
        print(f"❌ {module_path}: FAILED - {e}")
        return False

print("🧪 TESTING ALL IMPORTS...")
print("=" * 50)

# Test DAO imports
test_import("DAO/user_dao", "from DAO.user_dao import UserDAO")
test_import("DAO/portfolio_dao", "from DAO.portfolio_dao import PortfolioDAO") 
test_import("DAO/stock_dao", "from DAO.stock_dao import StockDAO")
test_import("DAO/transaction_dao", "from DAO.transaction_dao import TransactionDAO")

# Test Service imports
test_import("Service/user_service", "from Service.user_service import UserService")
test_import("Service/portfolio_service", "from Service.portfolio_service import PortfolioService")
test_import("Service/stock_service", "from Service.stock_service import StockService")
test_import("Service/transaction_service", "from Service.transaction_service import TransactionService")

# Test Client imports
test_import("Client/main", "from Client.main import MainCLI")
test_import("Client/portfolio_cli", "from Client.portfolio_cli import PortfolioCLI")
test_import("Client/stock_cli", "from Client.stock_cli import StockCLI")
test_import("Client/transaction_cli", "from Client.transaction_cli import TransactionCLI")

print("=" * 50)
print("🎉 Import testing complete!")