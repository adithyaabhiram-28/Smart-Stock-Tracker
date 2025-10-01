import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_supabase

class StockDAO:
    def __init__(self):
        self.sb = get_supabase()
    def add_stock(self,portfolio_id,symbol,price,quantity):
        resp = self.sb.table("stocks").insert({"portfolio_id" : portfolio_id , "symbol" : symbol , "price" : price , "quantity" : quantity}).execute()
        return resp.data
    def get_stock_by_portfolio(self,portfolio_id):
        resp = self.sb.table("stocks").select("*").eq("portfolio_id",portfolio_id).execute()
        return resp.data
    def get_stock_by_id(self,stock_id):
        resp = self.sb.table("stocks").select("*").eq("stock_id",stock_id).execute()
        return resp.data
    def update_stock(self, stock_id, price = None, quantity = None):
        data = {}
        if price is not None:
            data["price"] = price
        if quantity is not None:
            data["quantity"] = quantity
        resp = self.sb.table("stocks").update(data).eq("stock_id", stock_id).execute()
        return resp.data
    def delete_stock(self, stock_id):
        resp = self.sb.table("stocks").delete().eq("stock_id", stock_id).execute()
        return resp.data