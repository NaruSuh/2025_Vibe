import os
import requests
import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

class EmailService:
    """Brevo (formerly SendInBlue) 이메일 서비스 클래스"""

    def __init__(self):
        # API 키 가져오기
        self.api_key = self._get_api_key()
        if self.api_key:
            # Brevo API 설정
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key
            self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )
        else:
            self.api_instance = None

    def _get_api_key(self) -> Optional[str]:
        """환경변수 또는 Streamlit secrets에서 API 키 가져오기"""
        # 먼저 환경변수에서 확인
        api_key = os.getenv('BREVO_API_KEY')
        if api_key:
            return api_key

        # Streamlit secrets에서 확인 (안전하게)
        try:
            if hasattr(st, 'secrets'):
                return st.secrets.get('BREVO_API_KEY', None)
        except:
            pass

        return None

    def send_html_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """HTML 이메일 발송 (자동화용)"""
        if not self.api_instance:
            return False

        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={"email": "naru.seo.official@gmail.com", "name": "Clinical Psychology Hub"},
                subject=subject,
                html_content=html_content
            )

            response = self.api_instance.send_transac_email(send_smtp_email)
            return True

        except ApiException as e:
            print(f"❌ API Exception sending HTML email: {e}")
            return False
        except Exception as e:
            print(f"❌ Error sending HTML email: {e}")
            return False

    def send_research_alert(
        self,
        recipient_email: str,
        recipient_name: str,
        research_updates: Dict,
        professor_updates: List[Dict] = None
    ) -> bool:
        """연구 알림 이메일 발송"""

        if not self.api_instance:
            if hasattr(st, 'error'):
                st.error("❌ Brevo API 키가 설정되지 않았습니다.")
            print("❌ Brevo API 키가 설정되지 않았습니다.")
            return False

        try:
            # 이메일 HTML 템플릿 생성
            html_content = self._create_research_email_template(
                recipient_name, research_updates, professor_updates
            )

            # 이메일 발송 객체 생성
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": recipient_email, "name": recipient_name}],
                sender={"email": "naru.seo.official@gmail.com", "name": "Clinical Psychology Hub"},
                subject=f"📚 주간 임상심리학 연구 동향 - {datetime.now().strftime('%Y년 %m월 %d일')}",
                html_content=html_content
            )

            # 이메일 발송
            response = self.api_instance.send_transac_email(send_smtp_email)

            if hasattr(st, 'success'):
                st.success(f"✅ 이메일이 성공적으로 발송되었습니다! (ID: {response.message_id})")
            print(f"✅ 이메일 발송 성공 - ID: {response.message_id}")

            return True

        except ApiException as e:
            error_msg = f"❌ 이메일 발송 실패: {e.status} - {e.reason}"
            if hasattr(st, 'error'):
                st.error(error_msg)
            print(error_msg)
            return False
        except Exception as e:
            error_msg = f"❌ 예상치 못한 오류: {str(e)}"
            if hasattr(st, 'error'):
                st.error(error_msg)
            print(error_msg)
            return False

    def send_simple_test_email(self, recipient_email: str) -> bool:
        """간단한 테스트 이메일 발송"""
        if not self.api_instance:
            return False

        try:
            test_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": recipient_email}],
                sender={"email": "naru.seo.official@gmail.com", "name": "Clinical Psychology Hub"},
                subject="🧪 테스트 이메일 - Clinical Ph.D Machine",
                html_content="""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #4facfe;">✅ 테스트 이메일 성공!</h2>
                    <p>Clinical Ph.D Machine 플랫폼의 이메일 기능이 정상적으로 작동하고 있습니다.</p>
                    <p>이 이메일을 받으셨다면 Brevo API 연결이 성공한 것입니다! 🎉</p>
                </body>
                </html>
                """
            )

            response = self.api_instance.send_transac_email(test_email)
            return True

        except Exception as e:
            print(f"❌ 테스트 이메일 발송 실패: {e}")
            return False

    def send_professor_update(
        self,
        recipient_email: str,
        recipient_name: str,
        professor_name: str,
        updates: List[str]
    ) -> bool:
        """특정 교수 업데이트 이메일 발송"""

        if not self.api_instance:
            return False

        try:
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2E86AB;">👨‍🏫 {professor_name} 교수님 업데이트</h2>

                    <p>안녕하세요, {recipient_name}님!</p>

                    <p>관심을 가지고 계신 <strong>{professor_name}</strong> 교수님의 새로운 소식을 알려드립니다:</p>

                    <ul>
            """

            for update in updates:
                html_content += f"<li style='margin: 10px 0;'>{update}</li>"

            html_content += """
                    </ul>

                    <p style="margin-top: 30px;">
                        <a href="http://localhost:8501"
                           style="background-color: #2E86AB; color: white; padding: 12px 24px;
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            📱 플랫폼에서 더 보기
                        </a>
                    </p>

                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #666;">
                        이 이메일은 Clinical Psychology Platform에서 자동으로 발송되었습니다.
                    </p>
                </div>
            </body>
            </html>
            """

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": recipient_email, "name": recipient_name}],
                sender={"email": "noreply@clinicalpsychplatform.com", "name": "Clinical Psychology Platform"},
                subject=f"🔔 {professor_name} 교수님 업데이트 알림",
                html_content=html_content
            )

            response = self.api_instance.send_transac_email(send_smtp_email)
            return True

        except Exception as e:
            st.error(f"❌ 이메일 발송 실패: {str(e)}")
            return False

    def _create_research_email_template(
        self,
        recipient_name: str,
        research_updates: Dict,
        professor_updates: List[Dict] = None
    ) -> str:
        """연구 알림 이메일 HTML 템플릿 생성"""

        current_date = datetime.now().strftime('%Y년 %m월 %d일')

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4;">
            <div style="max-width: 700px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1);">

                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🧠 Clinical Psychology Platform</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">주간 연구 동향 리포트</p>
                </div>

                <!-- Content -->
                <div style="padding: 40px;">
                    <h2 style="color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 30px;">
                        안녕하세요, {recipient_name}님! 👋
                    </h2>

                    <p style="font-size: 16px; margin-bottom: 30px;">
                        {current_date} 임상심리학 분야의 최신 연구 동향을 정리해서 보내드립니다.
                    </p>
        """

        # 최신 논문 섹션
        if research_updates.get('papers'):
            html_content += """
                    <div style="background: #f8f9ff; padding: 25px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #667eea;">
                        <h3 style="color: #667eea; margin-top: 0;">📚 이번 주 주요 논문</h3>
            """
            for paper in research_updates['papers'][:5]:
                html_content += f"""
                        <div style="margin: 15px 0; padding: 15px; background: white; border-radius: 5px; border: 1px solid #e0e0e0;">
                            <h4 style="color: #333; margin: 0 0 8px 0; font-size: 16px;">{paper.get('title', '제목 없음')}</h4>
                            <p style="color: #666; margin: 0; font-size: 14px;">
                                <strong>저자:</strong> {paper.get('authors', '정보 없음')}<br>
                                <strong>저널:</strong> {paper.get('journal', '정보 없음')}
                            </p>
                        </div>
                """
            html_content += "</div>"

        # 관련 동영상 섹션
        if research_updates.get('videos'):
            html_content += """
                    <div style="background: #fff8f0; padding: 25px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #ff9500;">
                        <h3 style="color: #ff9500; margin-top: 0;">🎬 추천 동영상</h3>
            """
            for video in research_updates['videos'][:3]:
                html_content += f"""
                        <div style="margin: 15px 0; padding: 15px; background: white; border-radius: 5px; border: 1px solid #e0e0e0;">
                            <h4 style="color: #333; margin: 0 0 8px 0; font-size: 16px;">{video.get('title', '제목 없음')}</h4>
                            <p style="color: #666; margin: 5px 0; font-size: 14px;">
                                <strong>채널:</strong> {video.get('channel', '정보 없음')}<br>
                                <strong>조회수:</strong> {video.get('views', '정보 없음')}
                            </p>
                            <a href="{video.get('url', '#')}"
                               style="color: #ff9500; text-decoration: none; font-weight: bold;">
                                ▶️ 동영상 보기
                            </a>
                        </div>
                """
            html_content += "</div>"

        # 교수 업데이트 섹션
        if professor_updates:
            html_content += """
                    <div style="background: #f0f8f0; padding: 25px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #28a745;">
                        <h3 style="color: #28a745; margin-top: 0;">👨‍🏫 교수진 업데이트</h3>
            """
            for update in professor_updates:
                html_content += f"""
                        <div style="margin: 15px 0; padding: 15px; background: white; border-radius: 5px; border: 1px solid #e0e0e0;">
                            <h4 style="color: #333; margin: 0 0 8px 0;">{update.get('professor_name', '교수명 없음')}</h4>
                            <p style="color: #666; margin: 0; font-size: 14px;">{update.get('update_text', '업데이트 없음')}</p>
                        </div>
                """
            html_content += "</div>"

        # Footer
        html_content += f"""
                    <div style="text-align: center; margin: 40px 0 20px 0;">
                        <a href="http://localhost:8501"
                           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                  color: white; padding: 15px 30px; text-decoration: none;
                                  border-radius: 25px; display: inline-block; font-weight: bold;">
                            🔍 플랫폼에서 더 탐색하기
                        </a>
                    </div>

                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">

                    <div style="text-align: center; color: #666; font-size: 12px;">
                        <p>Clinical Psychology Platform | {current_date}</p>
                        <p>이 이메일은 자동으로 발송되었습니다. 수신거부를 원하시면 플랫폼 설정에서 변경해주세요.</p>
                    </div>
                </div>

            </div>
        </body>
        </html>
        """

        return html_content

    def test_email_connection(self) -> bool:
        """이메일 서비스 연결 테스트"""
        if not self.api_instance or not self.api_key:
            print("❌ API instance or key not available")
            return False

        try:
            # 계정 정보 조회로 연결 테스트
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key

            account_api = sib_api_v3_sdk.AccountApi(sib_api_v3_sdk.ApiClient(configuration))
            account_info = account_api.get_account()

            print(f"✅ API Connection successful - Email: {account_info.email}")
            return True

        except ApiException as e:
            print(f"❌ API Exception: {e.status} - {e.reason}")
            return False
        except Exception as e:
            print(f"❌ Connection Exception: {e}")
            return False

# 이메일 서비스 인스턴스 생성
email_service = EmailService()