import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_supabase

class TransactionDAO:
    def __init__(self):
        self.sb = get_supabase()
        self.table = "transactions"

    def add_transaction(self, portfolio_id, stock_id, trans_type, quantity, price):
        """
        Add a transaction (Buy/Sell) for a stock.
        trans_type must be 'Buy' or 'Sell'.
        """
        if trans_type not in ["Buy", "Sell"]:
            raise ValueError("Transaction type must be 'Buy' or 'Sell'")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")

        resp = self.sb.table(self.table).insert({
            "portfolio_id": portfolio_id,
            "stock_id": stock_id,
            "type": trans_type,
            "quantity": quantity,
            "price": price
        }).execute()
        return resp.data

    def get_transactions_by_portfolio(self, portfolio_id):
        """Get all transactions for a portfolio"""
        resp = self.sb.table(self.table).select("*").eq("portfolio_id", portfolio_id).execute()
        return resp.data

    def get_transactions_by_stock(self, stock_id):
        """Get all transactions for a specific stock"""
        resp = self.sb.table(self.table).select("*").eq("stock_id", stock_id).execute()
        return resp.data

    def get_transaction_by_id(self, trans_id):
        """Get a single transaction by ID"""
        resp = self.sb.table(self.table).select("*").eq("trans_id", trans_id).execute()
        return resp.data[0] if resp.data else None

    def delete_transaction(self, trans_id):
        """Delete a transaction (optional, if needed)"""
        resp = self.sb.table(self.table).delete().eq("trans_id", trans_id).execute()
        return resp.data
