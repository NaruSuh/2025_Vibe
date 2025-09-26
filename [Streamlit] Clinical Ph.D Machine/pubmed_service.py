import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import streamlit as st
from Bio import Entrez

class PubMedService:
    """PubMed API를 사용한 연구 논문 검색 서비스"""

    def __init__(self):
        # NCBI Entrez 이메일 설정 (필수)
        Entrez.email = "research@clinicalpsychplatform.com"
        Entrez.tool = "ClinicalPsychologyPlatform"

    def search_recent_papers(
        self,
        keywords: List[str],
        days_back: int = 7,
        max_results: int = 10
    ) -> List[Dict]:
        """최근 발표된 논문 검색"""

        try:
            # 검색 쿼리 생성
            search_query = self._build_search_query(keywords, days_back)

            # PubMed에서 논문 ID 검색
            search_results = Entrez.esearch(
                db="pubmed",
                term=search_query,
                retmax=max_results,
                sort="date"
            )

            search_data = Entrez.read(search_results)
            id_list = search_data["IdList"]

            if not id_list:
                return []

            # 논문 상세 정보 가져오기
            papers = self._fetch_paper_details(id_list)
            return papers

        except Exception as e:
            st.error(f"❌ PubMed 검색 중 오류 발생: {str(e)}")
            return []

    def _build_search_query(self, keywords: List[str], days_back: int) -> str:
        """검색 쿼리 생성"""

        # 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        date_range = f"({start_date.strftime('%Y/%m/%d')}[PDAT]:{end_date.strftime('%Y/%m/%d')}[PDAT])"

        # 키워드 조합
        if len(keywords) == 1:
            keyword_query = f'"{keywords[0]}"[Title/Abstract]'
        else:
            keyword_query = " OR ".join([f'"{kw}"[Title/Abstract]' for kw in keywords])
            keyword_query = f"({keyword_query})"

        # 임상심리학 관련 필터 추가
        clinical_filter = '("clinical psychology"[MeSH Terms] OR "psychotherapy"[MeSH Terms] OR "mental health"[MeSH Terms])'

        # 최종 쿼리 조합
        full_query = f"{keyword_query} AND {clinical_filter} AND {date_range}"

        return full_query

    def _fetch_paper_details(self, id_list: List[str]) -> List[Dict]:
        """논문 ID 리스트로부터 상세 정보 가져오기"""

        papers = []

        try:
            # 논문 상세 정보 요청
            fetch_results = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="xml"
            )

            xml_data = fetch_results.read()
            root = ET.fromstring(xml_data)

            for article in root.findall('.//PubmedArticle'):
                paper_info = self._parse_article_xml(article)
                if paper_info:
                    papers.append(paper_info)

        except Exception as e:
            st.error(f"❌ 논문 상세 정보 가져오기 실패: {str(e)}")

        return papers

    def _parse_article_xml(self, article) -> Optional[Dict]:
        """XML에서 논문 정보 파싱"""

        try:
            # 기본 정보 추출
            medline_citation = article.find('.//MedlineCitation')
            article_elem = medline_citation.find('.//Article')

            # 제목
            title_elem = article_elem.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "제목 없음"

            # 저자들
            authors = []
            author_list = article_elem.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name = author.find('.//LastName')
                    fore_name = author.find('.//ForeName')
                    if last_name is not None and fore_name is not None:
                        authors.append(f"{fore_name.text} {last_name.text}")

            authors_str = ", ".join(authors[:3])  # 처음 3명만
            if len(authors) > 3:
                authors_str += " et al."

            # 저널 정보
            journal_elem = article_elem.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else "저널 정보 없음"

            # 발행 날짜
            pub_date_elem = article_elem.find('.//PubDate')
            pub_date = self._extract_pub_date(pub_date_elem)

            # Abstract
            abstract_elem = article_elem.find('.//Abstract/AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else "초록 없음"

            # PMID
            pmid_elem = medline_citation.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else ""

            # PubMed URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

            return {
                "title": title,
                "authors": authors_str,
                "journal": journal,
                "pub_date": pub_date,
                "abstract": abstract[:200] + "..." if len(abstract) > 200 else abstract,
                "pmid": pmid,
                "url": url
            }

        except Exception as e:
            return None

    def _extract_pub_date(self, pub_date_elem) -> str:
        """발행 날짜 추출"""

        if pub_date_elem is None:
            return "날짜 정보 없음"

        try:
            year_elem = pub_date_elem.find('.//Year')
            month_elem = pub_date_elem.find('.//Month')
            day_elem = pub_date_elem.find('.//Day')

            year = year_elem.text if year_elem is not None else ""
            month = month_elem.text if month_elem is not None else ""
            day = day_elem.text if day_elem is not None else ""

            if year and month and day:
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            elif year and month:
                return f"{year}-{month.zfill(2)}"
            elif year:
                return year
            else:
                return "날짜 정보 없음"

        except:
            return "날짜 정보 없음"

    def search_professor_papers(
        self,
        professor_name: str,
        research_keywords: List[str],
        max_results: int = 5
    ) -> List[Dict]:
        """특정 교수의 최근 논문 검색"""

        try:
            # 교수 이름으로 검색 쿼리 생성
            name_parts = professor_name.split()
            if len(name_parts) >= 2:
                # "Smith J"[Author] 형태로 검색
                author_query = f'"{name_parts[-1]} {name_parts[0][0]}"[Author]'
            else:
                author_query = f'"{professor_name}"[Author]'

            # 연구 키워드 추가
            if research_keywords:
                keyword_query = " OR ".join([f'"{kw}"[Title/Abstract]' for kw in research_keywords])
                search_query = f"{author_query} AND ({keyword_query})"
            else:
                search_query = author_query

            # 최근 2년 논문으로 제한
            recent_filter = f"({(datetime.now() - timedelta(days=730)).strftime('%Y/%m/%d')}[PDAT]:{datetime.now().strftime('%Y/%m/%d')}[PDAT])"
            search_query += f" AND {recent_filter}"

            # 검색 실행
            search_results = Entrez.esearch(
                db="pubmed",
                term=search_query,
                retmax=max_results,
                sort="date"
            )

            search_data = Entrez.read(search_results)
            id_list = search_data["IdList"]

            if not id_list:
                return []

            papers = self._fetch_paper_details(id_list)
            return papers

        except Exception as e:
            st.error(f"❌ 교수 논문 검색 중 오류: {str(e)}")
            return []

    def get_trending_topics(self, days_back: int = 30) -> List[Dict]:
        """임상심리학 분야의 트렌딩 주제 분석"""

        trending_keywords = [
            "COVID-19 mental health",
            "digital therapeutics",
            "telehealth",
            "machine learning psychology",
            "precision medicine",
            "mindfulness intervention",
            "trauma therapy",
            "adolescent depression"
        ]

        trending_topics = []

        for keyword in trending_keywords:
            try:
                papers = self.search_recent_papers([keyword], days_back, 3)
                if papers:
                    trending_topics.append({
                        "keyword": keyword,
                        "paper_count": len(papers),
                        "recent_papers": papers
                    })
            except:
                continue

        # 논문 수가 많은 순으로 정렬
        trending_topics.sort(key=lambda x: x["paper_count"], reverse=True)
        return trending_topics[:5]

# PubMed 서비스 인스턴스
pubmed_service = PubMedService()