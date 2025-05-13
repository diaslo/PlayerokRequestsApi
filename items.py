import json
import tls_requests
from utils import globalheaders, load_cookies, get_username, api_url
from urllib.parse import urlparse


Priority_Status_Refill = {
    0: {
        "Min": 90,
        "Max": 499,
        "Status" : "1f00f21b-7768-62a0-296f-75a31ee8ce72"
    },
    1: {
        "Min": 500,
        "Max": 999,
        "Status" : "1f00f21b-776a-69b0-0118-32179c2cfc78"
    }
}


class PlayerokItemsApi:
    def __init__(self, cookies_file="cookies.json", logger=False):
        self.cookies = load_cookies(cookies_file)
        self.Logging = logger
        self.username, self.id = get_username(self.cookies)
  
    

    def get_categories_page(self, link: None):
        try:
            if link:
                parsed = urlparse(link)
                path_parts = [part for part in parsed.path.split('/') if part]
                params = {
                'operationName': 'GamePage',
                'variables': f'{{"slug":"{path_parts[1]}"}}',
                'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"30555c6386b910c25fc4f08c0e50296ecc38dd56b02b5919b3a71dce86b9b0bc"}}',
                }
                response = tls_requests.get(api_url, params=params, headers=globalheaders, cookies=self.cookies)

                if response.status_code == 200:
                    data = json.loads(response.text)
                    for categori in data['data']['game']['categories']:
                        if categori['slug'] == path_parts[2]:
                            return categori

        except Exception as e:
            pass
        return None

    def getObtainingTypeId(self, id: None):
        try:
            params = {
                'operationName': 'gameCategoryObtainingTypes',
                'variables': json.dumps({
                    "pagination": {"first": 16},
                    "filter": {"gameCategoryId": id}
                }),
                'extensions': json.dumps({
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "15b0991414821528251930b4c8161c299eb39882fd635dd5adb1a81fb0570aea"
                    }
                })
            }
            response = tls_requests.get(api_url, params=params, headers=globalheaders, cookies=self.cookies)
            if response.status_code == 200:
                data = json.loads(response.text)
                return data['data']['gameCategoryObtainingTypes']['edges'][0]['node']['id']
        except Exception as e:
            pass
        return None
    
    def getDatafielsID(self, gameCategoryId: None, ObtainingId: None):
        try:
            if gameCategoryId and ObtainingId:
                params = {
                    'operationName': 'gameCategoryDataFields',
                    'variables': json.dumps({
                        "pagination": {"first": 20},
                        "filter": {"gameCategoryId": gameCategoryId, "obtainingTypeId": ObtainingId, "type": "ITEM_DATA"}
                    }),
                    'extensions': json.dumps({
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "6fdadfb9b05880ce2d307a1412bc4f2e383683061c281e2b65a93f7266ea4a49"
                        }
                    })
                }

                response = tls_requests.get(api_url, params=params, headers=globalheaders, cookies=self.cookies)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    return data['data']['gameCategoryDataFields']['edges'][0]['node']['id']
        except Exception as e:
            pass
        return None


    def getgameCategoryOptions(self, id):
        try:
            if id:
                params = {
                    'operationName': 'gameCategoryOptions',
                    'variables': json.dumps({
                        "id": id
                    }),
                    'extensions': json.dumps({
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "ee8fdbe4e6fe6a924d5c19d5eed47bd9856f4dd16ee2e0e76841d0794a1f1b9b"
                        }
                    })
                }
                response = tls_requests.get(api_url, params=params, headers=globalheaders, cookies=self.cookies)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    return data

        except Exception as e:
            pass
        return None

    def create_sold_item(self, url_category, name_item, price, description, item_get, file_path):
        """создать новый товар для продажи"""
        dataPage = self.get_categories_page(url_category)
        ObtainingTypeId = self.getObtainingTypeId(dataPage['id'])

        operations = {
        "operationName": "createItem",
        "variables": {
            "input": {
                "gameCategoryId": dataPage['id'],
                "obtainingTypeId": ObtainingTypeId,
                "attributes": None,
                "name": name_item,
                "price": price,
                "description": description,
                "dataFields": [],
                "comment": item_get
            },
            "attachments": [None]
        },
        "query": """
            mutation createItem($input: CreateItemInput!, $attachments: [Upload!]!) {
                createItem(input: $input, attachments: $attachments) {
                ...RegularItem
                __typename
                }
            }

            fragment RegularItem on Item {
                ...RegularMyItem
                ...RegularForeignItem
                __typename
            }

            fragment RegularMyItem on MyItem {
                ...ItemFields
                prevPrice
                priority
                sequence
                priorityPrice
                statusExpirationDate
                comment
                viewsCounter
                statusDescription
                editable
                statusPayment {
                ...StatusPaymentTransaction
                __typename
                }
                moderator {
                id
                username
                __typename
                }
                approvalDate
                deletedAt
                createdAt
                updatedAt
                mayBePublished
                prevFeeMultiplier
                sellerNotifiedAboutFeeChange
                __typename
            }

            fragment ItemFields on Item {
                id
                slug
                name
                description
                rawPrice
                price
                attributes
                status
                priorityPosition
                sellerType
                feeMultiplier
                user {
                ...ItemUser
                __typename
                }
                buyer {
                ...ItemUser
                __typename
                }
                attachments {
                ...PartialFile
                __typename
                }
                category {
                ...RegularGameCategory
                __typename
                }
                game {
                ...RegularGameProfile
                __typename
                }
                comment
                dataFields {
                ...GameCategoryDataFieldWithValue
                __typename
                }
                obtainingType {
                ...GameCategoryObtainingType
                __typename
                }
                __typename
            }

            fragment ItemUser on UserFragment {
                ...UserEdgeNode
                __typename
            }

            fragment UserEdgeNode on UserFragment {
                ...RegularUserFragment
                __typename
            }

            fragment RegularUserFragment on UserFragment {
                id
                username
                role
                avatarURL
                isOnline
                isBlocked
                rating
                testimonialCounter
                createdAt
                supportChatId
                systemChatId
                __typename
            }

            fragment PartialFile on File {
                id
                url
                __typename
            }

            fragment RegularGameCategory on GameCategory {
                id
                slug
                name
                categoryId
                gameId
                obtaining
                options {
                ...RegularGameCategoryOption
                __typename
                }
                props {
                ...GameCategoryProps
                __typename
                }
                noCommentFromBuyer
                instructionForBuyer
                instructionForSeller
                useCustomObtaining
                autoConfirmPeriod
                autoModerationMode
                agreements {
                ...RegularGameCategoryAgreement
                __typename
                }
                feeMultiplier
                __typename
            }

            fragment RegularGameCategoryOption on GameCategoryOption {
                id
                group
                label
                type
                field
                value
                sequence
                valueRangeLimit {
                min
                max
                __typename
                }
                __typename
            }

            fragment GameCategoryProps on GameCategoryPropsObjectType {
                minTestimonials
                minTestimonialsForSeller
                __typename
            }

            fragment RegularGameCategoryAgreement on GameCategoryAgreement {
                description
                gameCategoryId
                gameCategoryObtainingTypeId
                iconType
                id
                sequence
                __typename
            }

            fragment RegularGameProfile on GameProfile {
                id
                name
                type
                slug
                logo {
                ...PartialFile
                __typename
                }
                __typename
            }

            fragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {
                id
                label
                type
                inputType
                copyable
                hidden
                required
                value
                __typename
            }

            fragment GameCategoryObtainingType on GameCategoryObtainingType {
                id
                name
                description
                gameCategoryId
                noCommentFromBuyer
                instructionForBuyer
                instructionForSeller
                sequence
                feeMultiplier
                agreements {
                ...RegularGameCategoryAgreement
                __typename
                }
                props {
                minTestimonialsForSeller
                __typename
                }
                __typename
            }

            fragment StatusPaymentTransaction on Transaction {
                id
                operation
                direction
                providerId
                status
                statusDescription
                statusExpirationDate
                value
                props {
                paymentURL
                __typename
                }
                __typename
            }

            fragment RegularForeignItem on ForeignItem {
                ...ItemFields
                __typename
            }
        """}


        

        map_data = {
            "1": ["variables.attachments.0"]
        }

        form_data = {
            'operations': json.dumps(operations),
            'map': json.dumps(map_data),
        }

        try:
            file_data = {
                '1': (file_path, open(file_path, 'rb'), 'image/jpeg')
            }
        except FileNotFoundError:
            pass

        response = tls_requests.post(
            'https://playerok.com/graphql',
            headers=globalheaders,
            cookies=self.cookies,
            data=form_data,
            files=file_data
        )
        response_json = response.json()
        return response_json


    def get_id_for_username(self, username):
        """получить айди пользователя по никнейму"""
        params = {
            "operationName": "user",
            "variables": f'{{"username":"{username}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"6dff0b984047e79aa4e416f0f0cb78c5175f071e08c051b07b6cf698ecd7f865"}}'
        }
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "access-control-allow-headers": "sentry-trace, baggage",
            "apollo-require-preflight": "true",
            "apollographql-client-name": "web",
            "referer": "https://playerok.com/profile/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }
        try:
            response = tls_requests.get(api_url, params=params, headers=headers, cookies=self.cookies)
            if response.status_code == 200:
                print("Запрос успешен!")
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                user_data = data["data"]["user"]
                user_id = user_data['id']
                return user_id
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None
        

    def fetch_lots(self, after_cursor=None):
        """захват завершенных лотов используется в функции self.get_all_lots"""
        variables = {
            "pagination": {"first": 16},
            "filter": {
                "userId": self.id,
                "status": ["DECLINED", "BLOCKED", "EXPIRED", "SOLD", "DRAFT"]
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
            response = tls_requests.get(api_url, headers=globalheaders, params=params, cookies=self.cookies)
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
            response = tls_requests.get(api_url, headers=globalheaders, params=params, cookies=self.cookies)
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

    def get_all_lots(self, search_filter: str = None) -> list[dict]:
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

    def copy_product(self, link):
        """получить информацию для выставления товара через ссылку"""
        if self.Logging:
            print("Начинаем копировать продукт")
        slug = link.replace("https://playerok.com/products", "").split('?')[0].strip('/')
        params = {
            "operationName": "item",
            "variables": f'{{"slug":"{slug}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}'
        }

        try:
            response = tls_requests.get(api_url, params=params, headers=globalheaders, cookies=self.cookies)
            if response.status_code == 200:
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                product_data = {
                    "title": data["data"]["item"]["name"],
                    "description": data["data"]["item"]["description"],
                    "rawprice": data["data"]["item"]["rawPrice"],
                    "price": data["data"]["item"]["price"],
                    "attachments": data["data"]["item"]["attachments"]
                }
                return product_data
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def increase_item_priority(self, item_id):
        """поднять товар по айди"""


        lots = self.all_exhibited_lots()
        lot = None
        for lot in lots:
            print(lot)
            if lot['id'] == item_id:
                lot = lot
        price = None
        if lot:
            price = lot['rawPrice']
        else:
            return None

        json_data = {
            "operationName": "increaseItemPriorityStatus",
            "variables": {
                "input": {
                    "priorityStatuses": [self.get_priority_status(price)],
                    "transactionProviderId": "LOCAL",
                    "transactionProviderData": {"paymentMethodId": None},
                    "itemId": f"{item_id}"
                }
            },
            "query": "mutation increaseItemPriorityStatus($input: PublishItemInput!) {\n  increaseItemPriorityStatus(input: $input) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  sequence\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}"
        }
        try:
            response = tls_requests.post(api_url, headers=globalheaders, cookies=self.cookies, json=json_data)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
        return None

    def get_priority_status(self, raw_price: int | float | None) -> str | None:
        if raw_price is None:
            return None
        
        try:
            for entry in Priority_Status_Refill.values():
                if entry["Min"] <= raw_price <= entry["Max"]:
                    return entry["Status"]
            return None
        except Exception as e:
            print(f"Error in get_priority_status: {e}")
            return None
    

    def refill_item(self, item_id):
        """возобновить товар по id (если он завершен)"""

        lots = self.get_all_lots()
        price = None
        if lots:
            for lot in lots:
                if lot.get('id') == item_id:
                    price = lot.get('rawPrice')
        else:  
            return None
        
        if not price:
            return None

        if item_id:
            json_data = {
                "operationName": "publishItem",
                "variables": {
                    "input": {
                        "priorityStatuses": [self.get_priority_status(price)],
                        "transactionProviderId": "LOCAL",
                        "transactionProviderData": {"paymentMethodId": None},
                        "itemId": f"{item_id}"
                    }
                },
                "query": "mutation publishItem($input: PublishItemInput!) {\n  publishItem(input: $input) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}"
            }
            try:
                response = tls_requests.post(api_url, headers=globalheaders, cookies=self.cookies, json=json_data)
                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    print(f"Ошибка {response.status_code}: {response.text}")
                    return None
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
        else:
            return None

    def get_product_data(self, link):
        """получить информацию о товаре через ссылку"""
        slug = link.replace("https://playerok.com/products", "").split('?')[0].strip('/')
        params = {
            "operationName": "item",
            "variables": f'{{"slug":"{slug}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}'
        }

        try:
            response = tls_requests.get(api_url, params=params, headers=globalheaders, cookies=self.cookies)
            if response.status_code == 200:
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                product_data = data
                return product_data
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def get_item_positioninfind(self, item_slug):
        """получить позицию предмета на рынке по slug"""
        params = {
            'operationName': 'item',
            'variables': f'{{"slug":"{item_slug}"}}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}',
        }
        response = tls_requests.get(api_url, params=params, cookies=self.cookies, headers=globalheaders)
        data = response.json()
        sequence = data['data']['item']['sequence']
        return sequence