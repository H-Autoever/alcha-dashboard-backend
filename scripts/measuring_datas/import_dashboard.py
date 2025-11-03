#!/usr/bin/env python3
"""
Grafana 대시보드 import 스크립트
"""

import json
import requests
import os

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_USER = os.getenv("GRAFANA_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GRAFANA_PASSWORD", "123qwe")

def import_dashboard():
    """대시보드를 Grafana에 import"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "grafana", "dashboards", "database-comparison.json")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        dashboard = json.load(f)
    
    # Grafana API 형식으로 변환
    payload = {
        "dashboard": dashboard,
        "overwrite": True,
        "inputs": []
    }
    
    url = f"{GRAFANA_URL}/api/dashboards/db"
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, auth=auth, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ 대시보드 import 성공!")
        print(f"   URL: {GRAFANA_URL}{result.get('url', '')}")
        print(f"   UID: {result.get('uid', '')}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 대시보드 import 실패: {e}")
        if hasattr(e.response, 'text'):
            print(f"   응답: {e.response.text}")
        return False

if __name__ == "__main__":
    import_dashboard()

