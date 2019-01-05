# -*- coding: utf-8 -*-
# 작성자 : 심보준(sragent@gmail.com)
# updated : 2018.02, jek.cl.nlp@gmail.com
""" '나무-잎' 패키지의 여러 모듈에서 공통으로 사용하는 자료구조와 함수를 모아 놓은 모듈 """

import codecs
import sys
import locale

# 색인 자료구조의 크기를 줄이기 위해서 구문 표지를 1글자 캐릭터로 치환하는 dictionary
# 구문 표지는 구문분석 말뭉치에서 4회이상 출현하는 것들로 한정지었다.
# 그 이하로 출현하는 구문 표지들은 대부분 오류이다.
# 예 > NP-SBJ, NPSBJ
tag2symbol = {'VP':'!', 'VP_MOD':'"', 'NP_SBJ':'#', 'NP_AJT':'$', 'NP':'%', 'S':'&', 'NP_OBJ':'\'', 'VNP':'*', 'NP_MOD':'+',
'AP':',', 'S_MOD':'-', 'NP_CNJ':'.', 'DP':'/', 'VNP_MOD':'0', 'NP_CMP':'1', 'L':'2', 'VP_CMP':'3', 'R':'4', 'VP_OBJ':'5',
'S_CMP':'6', 'VP_AJT':'7', 'VNP_CMP':'8', 'Q':'9', 'IP':':', 'X':';', 'NP_PRN':'<', 'VP_SBJ':'=', 'NP_INT':'>', 'R_PRN':'?',
'S_OBJ':'@', 'VNP_OBJ':'A', 'S_AJT':'B', 'X_CNJ':'C', 'X_CMP':'D', 'AP_MOD':'E', 'VNP_AJT':'F', 'X_SBJ':'G', 'X_AJT':'H',
'X_OBJ':'I', 'X_MOD':'J', 'VNP_SBJ':'K', 'S_SBJ':'L', 'S_PRN':'M', 'VP_PRN':'N', 'VP_CNJ':'O', 'Q_CMP':'P', 'VNP_CNJ':'Q',
'AP_AJT':'R', 'S_CNJ':'S', 'L_PRN':'T', 'LP':'U', 'VNP_PRN':'V', 'AP_OBJ':'W', 'AP_CMP':'X', 'S_INT':'Y', 'S-':'Z', 'Q_PRN':'[',
'AP_SBJ':'\\', 'VNP_INT':']', 'IP_CMP':'^', 'DP_AJT':'_', 'Q_MOD':'`', 'IP_INT':'a', 'LP_AJT':'b', 'VP_INT':'c', 'VCP':'d',
'Q_AJT':'e', 's':'f', 'VPP_CMP':'g', 'NP_ATJ':'h', 'DP_MOD':'i', 'LP_OBJ':'j', 'IP_AJT':'k', 'R_CNJ':'l', 'DP_OBJ':'m', 'LP_SBJ':'n', 'NPOBJ':'o'}

# tag2symbol dictionary를 되돌리기 위한 역 dictionary
symbol2tag = {'!':'VP', '"':'VP_MOD', '#':'NP_SBJ', '$':'NP_AJT', '%':'NP', '&':'S', '\'':'NP_OBJ', '*':'VNP', '+':'NP_MOD',
',':'AP', '-':'S_MOD', '.':'NP_CNJ', '/':'DP', '0':'VNP_MOD', '1':'NP_CMP', '2':'L', '3':'VP_CMP', '4':'R', '5':'VP_OBJ',
'6':'S_CMP', '7':'VP_AJT', '8':'VNP_CMP', '9':'Q', ':':'IP', ';':'X', '<':'NP_PRN', '=':'VP_SBJ', '>':'NP_INT', '?':'R_PRN',
'@':'S_OBJ', 'A':'VNP_OBJ', 'B':'S_AJT', 'C':'X_CNJ', 'D':'X_CMP', 'E':'AP_MOD', 'F':'VNP_AJT', 'G':'X_SBJ', 'H':'X_AJT',
'I':'X_OBJ', 'J':'X_MOD', 'K':'VNP_SBJ', 'L':'S_SBJ', 'M':'S_PRN', 'N':'VP_PRN', 'O':'VP_CNJ', 'P':'Q_CMP', 'Q':'VNP_CNJ',
'R':'AP_AJT', 'S':'S_CNJ', 'T':'L_PRN', 'U':'LP', 'V':'VNP_PRN', 'W':'AP_OBJ', 'X':'AP_CMP', 'Y':'S_INT', 'Z':'S-', '[':'Q_PRN',
'\\':'AP_SBJ', ']':'VNP_INT', '^':'IP_CMP', '_':'DP_AJT', '`':'Q_MOD', 'a':'IP_INT', 'b':'LP_AJT', 'c':'VP_INT', 'd':'VCP',
'e':'Q_AJT', 'f':'s', 'g':'VPP_CMP', 'h':'NP_ATJ', 'i':'DP_MOD', 'j':'LP_OBJ', 'k':'IP_AJT', 'l':'R_CNJ', 'm':'DP_OBJ', 'n':'LP_SBJ', 'o':'NPOBJ'}

def utf8Line(line):
    """ utf-8 인코딩 문자열을 현재 시스템의 표준출력 인코딩으로 변환한다.
    '나무-잎' 코어 라이브러리에서는 문자열을 utf-8 인코딩으로 저장한다.
    utf-8 라이브러러리에서 사용되는 문자열을 표준출력으로 출력하기 위해서는 이 함수를 이용한다.
    주로 테스트나 디버깅 용도로 사용된다. """
    '''
    uLine = line.decode('utf-8') #python2.x
    return codecs.encode(uLine, sys.stdout.encoding or locale.getpreferredencoding())
    '''
    return line #jek python3.x

def checkToken(token):
    """ 하나의 어절을 경우에 따라서는 또다시 어절분리를 해야 하는 경우가 있다.
    예를 들어 '우리나라(대한' 이런 어절은 '('를 기준으로 어절을 분리한다.
    세종 구문분석말뭉치 구축 지침에 따랐다. """
    tokens = []
    idx1= token.find('(')
    idx2 = token.find(')')
    if idx1 != -1 and (idx2 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx1])
        tokens.append('(')
        tokens = tokens + checkToken(token[idx1+1:])
        return tokens
    if idx2 != -1 and (idx1 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx2])
        tokens.append(')')
        tokens = tokens + checkToken(token[idx2+1:])
        return tokens

    idx1= token.find('[')
    idx2 = token.find(']')
    if idx1 != -1 and (idx2 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx1])
        tokens.append('[')
        tokens = tokens + checkToken(token[idx1+1:])
        return tokens
    if idx2 != -1 and (idx1 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx2])
        tokens.append(']')
        tokens = tokens + checkToken(token[idx2+1:])
        return tokens

    idx1= token.find('{')
    idx2 = token.find('}')
    if idx1 != -1 and (idx2 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx1])
        tokens.append('{')
        tokens = tokens + checkToken(token[idx1+1:])
        return tokens
    if idx2 != -1 and (idx1 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx2])
        tokens.append('}')
        tokens = tokens + checkToken(token[idx2+1:])
        return tokens

    idx1= token.find('“')
    idx2 = token.find('”')
    if idx1 != -1 and (idx2 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx1])
        tokens.append('“')
        tokens = tokens + checkToken(token[idx1+1:])
        return tokens
    if idx2 != -1 and (idx1 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx2])
        tokens.append('”')
        tokens = tokens + checkToken(token[idx2+1:])
        return tokens

    idx1= token.find('‘')
    idx2 = token.find('’')
    if idx1 != -1 and (idx2 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx1])
        tokens.append('‘')
        tokens = tokens + checkToken(token[idx1+1:])
        return tokens
    if idx2 != -1 and (idx1 == -1 or idx2 < idx1):
        tokens = tokens + checkToken(token[:idx2])
        tokens.append('’')
        tokens = tokens + checkToken(token[idx2+1:])
        return tokens

    idx1 = token.find('"')
    if idx1 != -1 and token.find('"', idx1+1) == -1:
        tokens = tokens + checkToken(token[:idx1])
        tokens.append('"')
        tokens = tokens + checkToken(token[idx1+1:])
        return tokens

    idx1 = token.find('\'')
    if idx1 != -1 and token.find('\'', idx1+1) == -1:
        tokens = tokens + checkToken(token[:idx1])
        tokens.append('\'')
        tokens = tokens + checkToken(token[idx1+1:])
        return tokens

    if token != '':
        tokens.append(token)
    return tokens


def highlightSentence(line, startIdx, endIdx):
    """ 시작어절 id, 끝어절 id를 입력으로 받아서 문장을 하일라이팅한다.
    하일라이팅 태그는 <!START>와 <!END> 이다.
    어절 분리규칙은 세종구문분석 말뭉치 구축 지침에 따랐다."""
    newSentence = ''
    splits = line.split()
    idx = 0
    for eoj in splits:
        tokens = checkToken(eoj)
        for token in tokens:
            if idx == startIdx:
                newSentence = newSentence + '<!START>'
            newSentence = newSentence + token
            if idx == endIdx:
                newSentence = newSentence + '<!END>'
            idx = idx + 1
        newSentence = newSentence + ' '
    if idx <= endIdx:
        newSentence = newSentence.strip() + '<!END>'
    return newSentence.strip()

class SyntaxInfo:
    """구문 구조 정보 1건을 저장하는 클래스
    구문구조를 1건씩 다룰 때,
    구문구조를 배열에 담아서 정렬하려고 할 때,
    호출자에 구문구조 배열을 반환할 때
    이 클래스로 생성한 객체가 사용된다.

    멤버 변수는 다음과 같다.
    info -- 구문구조 태그 예) NP(VP NP)
    sentenceId -- 해당 문장의 id, 구문분석 말뭉치의 문장에 각각 할당한 일련번호
    startIdx -- 구문 구조가 시작되는 어절의 인덱스 - 하일라이팅에 이용
    endIdx -- 구문 구조가 끝나는 어절의 인덱스 - 하일라이팅에 이용
    openPIdx -- startIdx 어절에서 구문구조가 몇번째 여는 괄호에서 시작되는가? - 하일라이팅에 이용
    closePIdx -- endIdx 어절에서 구문구조가 몇번째 닫는 괄호에서 끝나는가? - 하일라이팅에 이용 """
    def __init__(self, i, seId, si, ei, opi, cpi, tc):
        self.info = i
        self.sentenceId = seId
        self.startIdx = si
        self.endIdx = ei
        self.openPIdx = opi
        self.closePIdx = cpi
        self.tagCount = tc

    def __cmp__(self, other):
        """ 파이썬의 내장 배열 정렬함수를 이용하기 위한 override """
        if (self.endIdx - self.startIdx) == (other.endIdx - other.startIdx) :
            return cmp(self.sentenceId, other.sentenceId)
        return cmp(self.endIdx - self.startIdx, other.endIdx - other.startIdx)

    def __repr__(self):
        """ 구문구조 정보 출력을 위한 override
        """
        return self.info + " : " + "sentenceId = " + str(self.sentenceId) + " " + str(self.startIdx) + "~" + str(self.endIdx) + " tag_count = " + str(self.tagCount)

class SyntaxInfoList:
    """구문 구조 여러건을 저장하는 클래스
    SyntaxInfo 객체의 배열을 이용해서 색인 파일을 생성하려면 많은 메모리가 필요하고,
    수행속도가 매우 느리다.
    이 클래스는 여러개의 구문구조를 하나의 객체에 저장하여 메모리와 속도 효율성을 높이기 위해서 사용된다.
    예를 들어 NP(VP NP)에 해당되는 구문구조 1000건을 저장하기 위해
    SyntaxInfo 객체 1000개를 이용하는 대신,
    key : NP(VP NP) ---> 1개의 SyntaxInfoList 객체를 이용한다. 이 객체에는 크기가 1000인 5개의 배열이 사용된다.

    5개의 배열정보는 SyntaxInfo 클래스의 같은 이름 멤버 변수와 같은 용도이다. """
    def __init__(self):
        self.startIdxs = []
        self.endIdxs = []
        self.sentenceIds = []
        self.openPIdxs = []
        self.closePIdxs = []

    def addSyntaxInfo1(self, syntaxInfo):
        """ 리스트에 1개의 SyntaxInfo 객체를 추가하는 함수 """
        self.sentenceIds.append(syntaxInfo.sentenceId)
        self.startIdxs.append(syntaxInfo.startIdx)
        self.endIdxs.append(syntaxInfo.endIdx)
        self.openPIdxs.append(syntaxInfo.openPIdx)
        self.closePIdxs.append(syntaxInfo.closePIdx)

    def addSyntaxInfo2(self, sentenceId, startIdx, endIdx, openPIdx, closePIdx):
        """ 리스트에 구문 구조를 세부 정보를 이용하여 추가하는 함수 """
        self.sentenceIds.append(sentenceId)
        self.startIdxs.append(startIdx)
        self.endIdxs.append(endIdx)
        self.openPIdxs.append(openPIdx)
        self.closePIdxs.append(closePIdx)

    def length(self):
        return len(self.sentenceIds)

    def minWordCountIdx(self, minCount):
        """ 구문 구조 목록에서 단어 카운트가 minCount인 지점의 index를 반환하는 함수
        구문 구조가 단어 개수의 오름차순으로 정렬되어 있는 것을 가정한다.
        목록에서 micCount보다 단어 개수가 큰 정보가 없는 경우에 -1을 리턴한다. """

        if minCount < 2:
            return 0
        start = 0
        end = self.length()

        while True:
            mid = (end + start) / 2
            wordCount = self.endIdxs[mid] - self.startIdxs[mid] + 1
            if minCount == wordCount:
                while mid > 0:
                    wordCount = self.endIdxs[mid-1] - self.startIdxs[mid-1] + 1
                    if wordCount < minCount:
                        return mid
                    mid = mid - 1
                return 0
            elif minCount < wordCount:
                end = mid
                if end == 0:
                    return -1
            else:
                start = mid + 1
                if start == self.length():
                    return -1

    def printList(self):
        print('sentenceId   start   end')
        print('=========================')
        for i in range(self.length()):
            print('[%d, %d, %d, %d, %d]' % (self.sentenceIds[i], self.startIdxs[i], self.endIdxs[i], self.openPIdxs[i], self.closePIdxs[i]))
