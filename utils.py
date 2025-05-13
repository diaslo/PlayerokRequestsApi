import json
import tls_requests
globalheaders = {
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'access-control-allow-headers': 'sentry-trace, baggage',
    'apollo-require-preflight': 'true',
    'apollographql-client-name': 'web',
    'content-type': 'application/json',
    'origin': 'https://playerok.com',
    'priority': 'u=1, i',
    'referer': 'https://playerok.com/profile/',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"135.0.7049.115"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="135.0.7049.115", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'x-timezone-offset': '-180',
}
api_url = "https://playerok.com/graphql"

def load_cookies(cookies_file):
        cookies_dict = {}
        try:
            with open(cookies_file, "r", encoding="utf-8") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    cookies_dict[cookie["name"]] = cookie["value"]
        except Exception as e:
            print(f"Ошибка при загрузке куков: {e}")
        return cookies_dict

def get_username(cookies):
    """получить username и id пользователя (используется для получения в начале self.id, self.username)"""
    try:
        json_data = {
            'operationName': 'viewer',
            'variables': {},
            'query': 'query viewer {\n  viewer {\n    ...Viewer\n    __typename\n  }\n}\n\nfragment Viewer on User {\n  id\n  username\n  email\n  role\n  hasFrozenBalance\n  supportChatId\n  systemChatId\n  unreadChatsCounter\n  isBlocked\n  isBlockedFor\n  createdAt\n  lastItemCreatedAt\n  hasConfirmedPhoneNumber\n  canPublishItems\n  profile {\n    id\n    avatarURL\n    testimonialCounter\n    __typename\n  }\n  __typename\n}',
        }
        response = tls_requests.post(api_url, cookies=cookies, headers=globalheaders, json=json_data)
        try:
            data = response.json()
            viewer = data.get('data', {}).get('viewer', {})
            username = viewer.get('username', '')
            id = viewer.get('id', '')
            if not username:
                raise ValueError("Username not found")
            return username, id
        except Exception as e:
            print(f'Unsolved problem(Please pass this error to the API owner.) - ERROR: {e}')
    except ValueError as e:
        print(f"Ошибка данных: {e}")
        return '', ''
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return '', ''