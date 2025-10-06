import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import yaml

class SubscriberManager:
    """구독자 관리 시스템"""

    def __init__(self, data_file: str = "subscribers.json"):
        self.data_file = data_file
        self.subscribers = self._load_subscribers()

    def _load_subscribers(self) -> List[Dict]:
        """구독자 데이터 로드"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"구독자 데이터 로드 실패: {e}")
            return []

    def _save_subscribers(self):
        """구독자 데이터 저장"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.subscribers, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"구독자 데이터 저장 실패: {e}")

    def add_subscriber(
        self,
        email: str,
        name: str,
        interests: List[str],
        frequency: str = "weekly"
    ) -> bool:
        """새 구독자 추가"""

        # 중복 확인
        if self.get_subscriber(email):
            return False

        subscriber = {
            "email": email,
            "name": name,
            "interests": interests,
            "frequency": frequency,
            "subscribed_date": datetime.now().isoformat(),
            "last_sent": None,
            "active": True,
            "preferences": {
                "include_papers": True,
                "include_videos": True,
                "include_trends": True,
                "max_papers": 5,
                "max_videos": 3
            }
        }

        self.subscribers.append(subscriber)
        self._save_subscribers()
        return True

    def get_subscriber(self, email: str) -> Optional[Dict]:
        """이메일로 구독자 조회"""
        for subscriber in self.subscribers:
            if subscriber["email"] == email:
                return subscriber
        return None

    def update_subscriber(self, email: str, updates: Dict) -> bool:
        """구독자 정보 업데이트"""
        for i, subscriber in enumerate(self.subscribers):
            if subscriber["email"] == email:
                self.subscribers[i].update(updates)
                self._save_subscribers()
                return True
        return False

    def remove_subscriber(self, email: str) -> bool:
        """구독자 제거"""
        for i, subscriber in enumerate(self.subscribers):
            if subscriber["email"] == email:
                self.subscribers.pop(i)
                self._save_subscribers()
                return True
        return False

    def get_active_subscribers(self, frequency: str = None) -> List[Dict]:
        """활성 구독자 목록 조회"""
        active_subs = [s for s in self.subscribers if s.get("active", True)]

        if frequency:
            active_subs = [s for s in active_subs if s.get("frequency") == frequency]

        return active_subs

    def get_subscribers_by_interest(self, interest: str) -> List[Dict]:
        """관심 분야별 구독자 조회"""
        return [
            s for s in self.subscribers
            if s.get("active", True) and interest.lower() in [i.lower() for i in s.get("interests", [])]
        ]

    def mark_sent(self, email: str):
        """이메일 발송 완료 마킹"""
        self.update_subscriber(email, {"last_sent": datetime.now().isoformat()})

    def get_statistics(self) -> Dict:
        """구독자 통계"""
        total = len(self.subscribers)
        active = len([s for s in self.subscribers if s.get("active", True)])

        # 관심 분야별 통계
        interests_count = {}
        for subscriber in self.subscribers:
            if subscriber.get("active", True):
                for interest in subscriber.get("interests", []):
                    interests_count[interest] = interests_count.get(interest, 0) + 1

        # 구독 주기별 통계
        frequency_count = {}
        for subscriber in self.subscribers:
            if subscriber.get("active", True):
                freq = subscriber.get("frequency", "weekly")
                frequency_count[freq] = frequency_count.get(freq, 0) + 1

        return {
            "total_subscribers": total,
            "active_subscribers": active,
            "interests": interests_count,
            "frequencies": frequency_count
        }

    def export_to_yaml(self, output_file: str = "subscribers.yml"):
        """구독자 데이터를 YAML로 내보내기 (GitHub Actions 사용)"""
        try:
            # GitHub Actions에서 사용할 수 있는 형태로 변환
            export_data = {
                "subscribers": self.get_active_subscribers(),
                "last_export": datetime.now().isoformat(),
                "total_count": len(self.get_active_subscribers())
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)

            return True
        except Exception as e:
            print(f"YAML 내보내기 실패: {e}")
            return False

# 전역 구독자 관리자 인스턴스
subscriber_manager = SubscriberManager()