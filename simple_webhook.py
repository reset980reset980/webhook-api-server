from flask import Flask, request, jsonify
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)

# 설정: 환경변수 또는 기본값
N8N_GOOGLE_CLOUD_URL = os.getenv('N8N_GOOGLE_CLOUD_URL', '')
N8N_RAILWAY_URL = os.getenv('N8N_RAILWAY_URL', '')
SAVE_TO_FILE = os.getenv('SAVE_TO_FILE', 'true').lower() == 'true'

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "running",
        "message": "API 서버가 정상 작동 중입니다!",
        "config": {
            "google_cloud_n8n": bool(N8N_GOOGLE_CLOUD_URL),
            "railway_n8n": bool(N8N_RAILWAY_URL),
            "save_to_file": SAVE_TO_FILE
        }
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # 받은 데이터
        data = request.json
        
        # 현재 시간 추가
        data['received_at'] = datetime.now().isoformat()
        
        print(f"데이터 받음: {data}")
        
        results = []
        
        # 1. 파일로 저장 (샌드박스용)
        if SAVE_TO_FILE:
            try:
                with open('webhook_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                results.append({"method": "file", "status": "success"})
                print("파일 저장 완료")
            except Exception as e:
                results.append({"method": "file", "status": "error", "error": str(e)})
        
        # 2. 구글클라우드 n8n으로 전송
        if N8N_GOOGLE_CLOUD_URL:
            try:
                response = requests.post(N8N_GOOGLE_CLOUD_URL, json=data, timeout=30)
                results.append({
                    "method": "google_cloud_n8n", 
                    "status": "success", 
                    "response_code": response.status_code
                })
                print(f"구글클라우드 n8n 전송 완료: {response.status_code}")
            except Exception as e:
                results.append({"method": "google_cloud_n8n", "status": "error", "error": str(e)})
        
        # 3. Railway n8n으로 전송
        if N8N_RAILWAY_URL:
            try:
                response = requests.post(N8N_RAILWAY_URL, json=data, timeout=30)
                results.append({
                    "method": "railway_n8n", 
                    "status": "success", 
                    "response_code": response.status_code
                })
                print(f"Railway n8n 전송 완료: {response.status_code}")
            except Exception as e:
                results.append({"method": "railway_n8n", "status": "error", "error": str(e)})
        
        return jsonify({
            "status": "success", 
            "message": "데이터 처리 완료",
            "received_data": data,
            "processing_results": results
        })
    
    except Exception as e:
        print(f"에러 발생: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # 개발용
    app.run(host='0.0.0.0', port=5000, debug=True)
