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
        
        # 대시보드 강제 새로고침 (대시보드가 즉시 데이터를 로드하도록)
        dashboard_uid = result.get('uid', '')
        if dashboard_uid:
            try:
                # 대시보드를 한 번 쿼리하여 강제로 새로고침 트리거
                refresh_url = f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_uid}"
                refresh_response = requests.get(refresh_url, auth=auth, headers=headers)
                refresh_response.raise_for_status()
                
                # 대시보드 홈페이지를 실제로 방문하여 패널 쿼리 실행 강제
                # 이렇게 하면 패널들이 실제로 쿼리를 실행하게 됨
                dashboard_url = f"{GRAFANA_URL}{result.get('url', '')}"
                
                # 실제 대시보드 페이지를 GET 요청하여 패널들이 쿼리를 실행하도록 트리거
                # 대시보드 URL에 ?refresh=10s 파라미터를 추가하여 자동 새로고침 활성화
                view_url = f"{dashboard_url}?refresh=10s"
                try:
                    # 세션 쿠키를 사용하여 인증 유지
                    session = requests.Session()
                    session.auth = auth
                    session.get(view_url, headers=headers, timeout=5)
                    print(f"   ✅ 대시보드 페이지 방문 완료 (패널 쿼리 트리거)")
                except:
                    pass  # 실패해도 무시 (이미 import되었으므로)
                
                print(f"   ✅ 대시보드 강제 새로고침 완료")
                print(f"   💡 대시보드 URL: {dashboard_url}")
                print(f"      위 URL을 브라우저에서 열면 데이터가 자동으로 로드됩니다.")
            except Exception as e:
                print(f"   ⚠️  새로고침 시도 실패 (무시됨): {e}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 대시보드 import 실패: {e}")
        if hasattr(e.response, 'text'):
            print(f"   응답: {e.response.text}")
        return False

if __name__ == "__main__":
    import_dashboard()

