from flask import Flask, request
import requests
import json

app = Flask(__name__)

HUBSPOT_API_KEY = 'YOUR_HUBSPOT_API_KEY'
FREEE_ACCESS_TOKEN = 'YOUR_FREEE_ACCESS_TOKEN'
FREEE_COMPANY_ID = 'YOUR_FREEE_COMPANY_ID'

def create_freee_document(document_type, document_data):
    """
    freee APIを使用してドキュメント（見積書または発注書）を作成する関数
    """
    headers = {'Authorization': f'Bearer {FREEE_ACCESS_TOKEN}', 'Content-Type': 'application/json'}
    freee_url = f'https://api.freee.co.jp/api/1/{document_type}'
    response = requests.post(freee_url, headers=headers, data=json.dumps(document_data))
    return response.status_code

@app.route('/webhook', methods=['POST'])
def webhook():
    # HubSpotからのWebhookを受信
    data = request.json
    deal_id = data['objectId']

    # HubSpot APIを使用して取引データを取得
    hubspot_url = f'https://api.hubapi.com/crm/v3/objects/deals/{deal_id}?hapikey={HUBSPOT_API_KEY}'
    response = requests.get(hubspot_url)
    deal_data = response.json()
    deal_name = deal_data['properties']['dealname']

    # 見積書データと発注書データの共通部分を定義
    common_data = {
        'company_id': FREEE_COMPANY_ID,
        'issue_date': '2024-03-31',
        'due_date': '2024-04-30',
        'title': deal_name,
        'description': 'ドキュメントの説明',
        'details': [
            {
                'type': 'service',
                'name': 'サービスA',
                'unit_price': 10000,
                'quantity': 2
            }
        ]
    }

    # 見積書データを作成
    quote_status_code = create_freee_document('quotations', common_data)
    print(f'見積書作成結果: {quote_status_code}')

    # 発注書データを作成
    order_status_code = create_freee_document('orders', common_data)
    print(f'発注書作成結果: {order_status_code}')

    return 'Webhook received', 200

if __name__ == '__main__':
    app.run(port=5000)
