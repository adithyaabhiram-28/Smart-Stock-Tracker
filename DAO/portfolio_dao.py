import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_supabase

class PortfolioDAO:
    def __init__(self):
        self.sb = get_supabase()
    def create_portfolio(self,user_id,portfolio_name):
        resp = self.sb.table("portfolios").insert({"user_id" : user_id , "portfolio_name" : portfolio_name}).execute()
        return resp
    def get_portfolio_by_user(self,user_id):
        resp = self.sb.table("portfolios").select("*").eq("user_id", user_id).execute()
        return resp.data
    def get_portfolio_by_id(self,portfolio_id):
        resp = self.sb.table("portfolios").select("*").eq("portfolio_id", portfolio_id).execute()
        return resp.data[0] if resp.data else None
    def update_portfolio(self,portfolio_id,portfolio_name):
        resp = self.sb.table("portfolios").update({"portfolio_name" : portfolio_name}).eq("portfolio_id", portfolio_id).execute()
        return resp.data
    def delete_portfolio(self,portfolio_id):
        resp = self.sb.table("portfolios").delete().eq("portfolio_id", portfolio_id).execute()
        return resp