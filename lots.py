import json
import tls_requests
from utils import globalheaders, load_cookies, api_url, get_username
from urllib.parse import urlparse

class PlayerokLotsApi:
    def __init__(self, cookies_file="cookies.json", logger=False):
        self.cookies = load_cookies(cookies_file)
        self.Logging = logger
        self.api_url = api_url
        self.username, self.id = get_username(self.cookies)

    def fetch_lots(self, after_cursor=None):
        """захват завершенных лотов используется в функции self.get_all_lots"""
        variables = {
            "pagination": {"first": 16},
            "filter": {
                "userId": self.id,
                "status": ["EXPIRED", "SOLD", "DRAFT"]
            }
        }
        if after_cursor:
            variables["pagination"]["after"] = after_cursor
        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "d79d6e2921fea03c5f1515a8925fbb816eacaa7bcafe03eb47a40425ef49601e"
            }
        }
        params = {
            "operationName": "items",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions)
        }
        try:
            response = tls_requests.get(self.api_url, headers=globalheaders, params=params, cookies=self.cookies)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

    def fetch_exhibited_lots(self, userid=None, after_cursor=None):
        """захват выставленных лотов"""
        variables = {"pagination": {"first": 16}, "filter": {"userId": f"{self.id if not userid else userid}", "status": ["APPROVED"]}}
        if after_cursor:
            variables["pagination"]["after"] = after_cursor
        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "d79d6e2921fea03c5f1515a8925fbb816eacaa7bcafe03eb47a40425ef49601e"
            }
        }
        params = {
            "operationName": "items",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions)
        }
        try:
            response = tls_requests.get(self.api_url, headers=globalheaders, params=params, cookies=self.cookies)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

    def all_exhibited_lots(self, userid: int = None, search_filter: str = None) -> list[dict]:
        """Все выставленные лоты (можно смотреть у других по userid). 
        Если не указать id - будут показаны свои лоты.
        Параметр search_filter осуществляет поиск по всем текстовым полям лота."""
        
        lots = []
        try:
            response = self.fetch_exhibited_lots(userid)
            if not response or 'data' not in response:
                return lots

            for edge in response['data']['items']['edges']:
                node = edge.get('node', {})
                if search_filter:
                    if any(search_filter.lower() in str(value).lower() 
                        for value in node.values() 
                        if isinstance(value, (str, int, float))):
                        lots.append(node)
                else:
                    lots.append(node)

            while True:
                page_info = response['data']['items']['pageInfo']
                if not page_info['hasNextPage'] or not page_info['endCursor']:
                    break

                response = self.fetch_exhibited_lots(
                    userid, 
                    after_cursor=page_info['endCursor']
                )
                
                if not response or 'data' not in response:
                    break

                for edge in response['data']['items']['edges']:
                    node = edge.get('node', {})
                    if search_filter:
                        if any(search_filter.lower() in str(value).lower() 
                            for value in node.values() 
                            if isinstance(value, (str, int, float))):
                            lots.append(node)
                    else:
                        lots.append(node)

            return lots
        
        except Exception as e:
            print(f"Ошибка при получении лотов: {e}")
            return lots

    def get_all_ended_lots(self, search_filter: str = None) -> list[dict]:
        """получить информацию по всем завершённым лотам"""
        after_cursor = None
        all_lots = []

        while True:
            response = self.fetch_lots(after_cursor=after_cursor)

            if not response or "data" not in response or "items" not in response["data"]:
                break

            items = response["data"]["items"]
            edges = items.get("edges", [])
            page_info = items.get("pageInfo", {})

            for edge in edges:
                if not edge.get("node"):
                    continue

                if search_filter:
                    node = edge["node"]
                    if any(search_filter.lower() in str(value).lower()
                           for value in node.values()
                           if isinstance(value, (str, int, float))):
                        all_lots.append(node)
                else:
                    all_lots.append(edge["node"])

            if not page_info.get("hasNextPage") or not page_info.get("endCursor"):
                break

            after_cursor = page_info["endCursor"]

        return all_lots