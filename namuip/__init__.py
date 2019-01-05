# -*- coding: utf-8 -*-
# 작성자 : 심보준(sragent@gmail.com)
# 추가 : 은경(jek.cl.nlp@gmail.com), 2017.02. Compressor

""" '나무-잎' 색인 및 검색 core 라이브러리 패키지

'나무-잎'은 21세기 세종계획의 구문분석 말뭉치에서 용례를 검색하는 프로그램이다.

이 패키지는 5개의 sub 모듈로 구성되어 있다.

Indexer(색인기) -- 구문분석 말뭉치를 문석하여 검색에 효율적인 색인 자료 구조를 만들고
           색인 파일을 만드는 모듈

Storage(저장소) -- 구문분석 말뭉치의 본문을 저장하는 자료 구조를 만들고 저장 파일을
           만드는 모듈

Searcher(검색기) -- Front 모듈의 입력을 받아서 검색 결과 목록을 만들어 반환하는 모듈

common -- 여러 sub 모듈에서 공통으로 사용하는 자료구조와 함수를 모아놓은 모듈

Compressor(압축기) -- 구문 축약 모듈 : 구구조 규칙 및 말뭉치 규칙에 의해 축약한다. """

from namuip.document import *
from namuip.index import *
from namuip.search import *
from namuip.common import *
from namuip.compress import *
'''
from document import Storage
from index import Indexer
from search import Searcher
from common import *
from compress import Compressor
'''
