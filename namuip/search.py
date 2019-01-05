# -*- coding: utf-8 -*-
# 작성자 : 심보준(sragent@gmail.com)
# 2018.02: 은경(jek.cl.nlp@gmail.com)
''' Search from indexed data in naive texts instead of c-struct binary
Originally there were hightlight errors. Need to be corrected '''

from namuip.index import Indexer
from namuip.index import SyntaxInfoList
from namuip.document import Storage
from namuip.common import *

'''#unit test under namuip module
from index import Indexer
from index import SyntaxInfoList
from document import Storage
from common import *
'''
import struct
import array
import sys

class Searcher:
    """ '나무-잎' 패키지 검색기 클래스
    인스턴스를 생성하면 구문구조 문장 저장소 파일과 색인 파일을 메모리에 적재한다.

    색인은 key(string) ---> SyntaxInfoList 형식으로 된 dictionary 이다.
    호출모듈에서 입력한 key가 dictionary에 있으면 SyntaxInfoList를 배열로 변환하여 반환한다. """
    def __init__(self, homeDir):
        """ 저장소 파일과 색인 파일을 메모리에 적재한다.
        """
        print(('색인 적재 시작'))
        self.sentenceStorage = Storage()
        self.storage = self.sentenceStorage.load(homeDir + '/storage.data')
        self.indexMap = None
        self.__loadIndex(homeDir + '/index.data')
        print(('\n색인 적재 완료'))

    def __loadIndex(self, fileName): #by jek
        rf = open(fileName, encoding='utf-8')
        keyCount = int(rf.readline().strip())
        totKeyLength = int(rf.readline().strip())
        totSyntaxInfoCount = int(rf.readline().strip())
        keyLengthArray = rf.readline().strip().split(',')
        keyCharArray = list(rf.readline().strip())
        syntaxInfoCountArray = rf.readline().strip().split(',')
        syntaxInfoArray = rf.readline().strip().split('|')
        rf.close()

        # 위의 파일에서 읽은 정보를 바탕으로 indexMap를 채운다.
        self.indexMap = {}
        keyStart = 0

        for i in range(keyCount) :
            if i % 10000 == 0:
                sys.stdout.write('[%d]' % i)
                sys.stdout.flush()
            keyEnd = keyStart + int(keyLengthArray[i])
            key = ''.join(keyCharArray[keyStart:keyEnd])
            keyStart = keyEnd
            syntaxInfoCount = int(syntaxInfoCountArray[i])
            #print(i, key, keyStart, keyEnd)
            #print(int(syntaxInfoCountArray[i]))
            syntaxInfoList = SyntaxInfoList()
            for j in range(syntaxInfoCount):
                i_tuple = syntaxInfoArray[i+j].strip('()').split(',')
                sentenceId = int(i_tuple[0])
                startIdx = int(i_tuple[1])
                endIdx = int(i_tuple[2])
                openPIdx = int(i_tuple[3])
                closePIdx = int(i_tuple[4])
                syntaxInfoList.addSyntaxInfo2(sentenceId, startIdx, endIdx, openPIdx, closePIdx)
            self.indexMap[key] = syntaxInfoList
            #print(i, key, syntaxInfoList)
        return

    def __loadIndex0(self, fileName): # by Simbj
        """ 색인을 메모리(indexMap dictionary)에 적재한다.
        Indexer의 __writeToFile 함수와 정보 저장 순서가 호환되어야 한다. """
        rfp = open(fileName, 'rb')
        # key 개수
        keyCount, = struct.unpack('i', rfp.read(struct.calcsize('i')))
        print(('전체 : %d개 색인 정보' % keyCount))
        # key 문자열의 길이의 총합
        # key 문자열을 한꺼번에 읽기 위해 필요
        totKeyLength, = struct.unpack('l', rfp.read(struct.calcsize('l')))
        # key 한개에 여러개의 구문정보가 들어간다.
        # 구문정보 개수의 총합
        # 구문정보를 한꺼번에 읽기 위해 필요
        totSyntaxInfoCount, = struct.unpack('l', rfp.read(struct.calcsize('l')))

        keyLengthArray = array.array('i')
        #jekkeyCharArray = array.array('c')
        keyCharArray = array.array('u')
        syntaxInfoCountArray = array.array('i')
        syntaxInfoArray = array.array('i')

        # 각 key마다 key길이
        keyLengthArray.fromfile(rfp, keyCount)
        # 모든 key를 붙여서 하나의 정보로 읽는다.
        keyCharArray.fromfile(rfp, totKeyLength)
        # 각 key마다 구문정보 개수
        syntaxInfoCountArray.fromfile(rfp, keyCount)
        # 모든 구문정보를 한번에 읽는다.
        #jeksyntaxInfoArray.fromfile(rfp, totSyntaxInfoCount * 5)
        syntaxInfoArray.fromfile(rfp, totSyntaxInfoCount )

        # 위의 파일에서 읽은 정보를 바탕으로 indexMap dictionary 정보를 채운다.
        self.indexMap = {}
        keyStart = 0
        infoStart = 0

        for i in range(keyCount) :
            if i % 10000 == 0:
                sys.stdout.write('[%d]' % i)
                sys.stdout.flush()
            keyEnd = keyStart + keyLengthArray[i]
            key = keyCharArray[keyStart:keyEnd].tostring()
            keyStart = keyEnd
            syntaxInfoCount = syntaxInfoCountArray[i]
            syntaxInfoList = SyntaxInfoList()
            for j in range(syntaxInfoCount):
                sentenceId = syntaxInfoArray[infoStart + j * 5 + 0]
                startIdx = syntaxInfoArray[infoStart + j * 5 + 1]
                endIdx = syntaxInfoArray[infoStart + j * 5 + 2]
                openPIdx = syntaxInfoArray[infoStart + j * 5 + 3]
                closePIdx = syntaxInfoArray[infoStart + j * 5 + 4]
                syntaxInfoList.addSyntaxInfo2(sentenceId, startIdx, endIdx, openPIdx, closePIdx)
            infoStart = infoStart + syntaxInfoCount * 5
            self.indexMap[key] = syntaxInfoList
        return

    def search(self, query, start, count, minWordCount=1):
        """구문구조 query를 입력 받아서 결과 SyntaxInfo의 list를 반환한다.
        query -- 입력 쿼리 예) VP(NP VP)
        start -- 결과중 몇번째서 부터?
        count -- 결과 몇개?
        minWordCount -- 어절 개수가 특정개수 이상인 결과만을 얻고 싶을때 사용하는 파라미터

        예외가 발생하면 빈 리스트를 반환한다. """
        query = query.upper()
        # 색인의 key가 태그를 대표 캐릭터로 치환한 상태이므로 쿼리도 대표 캐릭터로 치환한다.
        # tag2symbol dictionary를 이용한다.
        newQuery = ''
        if query.find('(') == -1:
            if query not in tag2symbol:
                return []
            newQuery = tag2symbol[query]
        else:
            idx1 = 0
            for i in range(len(query)):
                if query[i] == '(' or query[i] == ')' or query[i] == ' ':
                    if idx1 != i:
                        if query[idx1:i] not in tag2symbol:
                            return []
                        tagsymbol = tag2symbol[query[idx1:i]]
                        newQuery = newQuery + tagsymbol
                    newQuery = newQuery + query[i]
                    idx1 = i + 1
        newQuery = newQuery.replace(' ', '') #XXX:
        #print(newQuery) #jek
        if newQuery not in self.indexMap:
            return []
        syntaxInfoList = self.indexMap[newQuery]
        results = []

        # 어절 개수가 2개 이상인 경우를 원할 때
        if minWordCount > 1:
            # 색인은 어절개수의 오름차순으로 정렬되어 있고
            # minIdx 번째 부터 어절개수가 minwordCount개 이상이다.
            minIdx = syntaxInfoList.minWordCountIdx(minWordCount)
            # minWordCount 보다 어절 개수가 많은 결과가 없는 경우
            # 빈 리스트 반환
            if minIdx == -1:
                return []
            else:
                start = start + syntaxInfoList.minWordCountIdx(minWordCount)

        for i in range(start, start+count):
            if i == syntaxInfoList.length():
                break
            syntaxInfo = SyntaxInfo('', syntaxInfoList.sentenceIds[i],
                            syntaxInfoList.startIdxs[i],
                            syntaxInfoList.endIdxs[i],
                            syntaxInfoList.openPIdxs[i],
                            syntaxInfoList.closePIdxs[i], 0)
            sentence = self.sentenceStorage[syntaxInfo.sentenceId]
            # 매칭된 구문정보 부분에 하일라이팅 처리
            # startIdx번째 어절의 openPIdx번째 여는 괄호부터
            # endIdx번째 어절의 closePIdx번째 닫는 괄호
            # 0번째 라인은 문장
            # 1번째 라인부터가 구문 구조, 즉 1번째 라인이 0번째 어절에 대한 정보
            splits = sentence.split('\n')
            # 하일라이팅. 단, 문장 맨앞의 '; ' 부분은 자른다.
            newSentence = '%s\n' % highlightSentence(splits[0][2:], syntaxInfo.startIdx, syntaxInfo.endIdx)
            comp_sent = '' #jek

            for j in range(1, len(splits)):
                if j-1 == syntaxInfo.startIdx:
                    pos = -1
                    for k in range(syntaxInfo.openPIdx+1):
                        pos = splits[j].find('(', pos+1)
                    splits[j] = '%s<!START>%s' % (splits[j][:pos], splits[j][pos:])
                if j-1 == syntaxInfo.endIdx:
                    pos = -1
                    for k in range(syntaxInfo.closePIdx+1):
                        pos = splits[j].find(')', pos+1)
                    splits[j] = '%s<!END>%s' % (splits[j][:pos+1], splits[j][pos+1:])
                newSentence = newSentence + splits[j] + '\n'
            results.append((syntaxInfo, newSentence))

        return results

    def searchAll(self, query, start, count, minWordCount=1):
        """구문구조 query를 입력 받아서 결과 SyntaxInfo의 list를 반환한다.
        query -- 입력 쿼리 예) VP(NP VP)
        start -- 결과중 몇번째서 부터?
        count -- 결과 몇개?
        minWordCount -- 어절 개수가 특정개수 이상인 결과만을 얻고 싶을때 사용하는 파라미터

        예외가 발생하면 빈 리스트를 반환한다. """
        query = query.upper()
        # 색인의 key가 태그를 대표 캐릭터로 치환한 상태이므로 쿼리도 대표 캐릭터로 치환한다.
        # tag2symbol dictionary를 이용한다.
        newQuery = ''
        if query.find('(') == -1:
            '''jekif query not in tag2symbol:
                return []
            newQuery = tag2symbol[query]'''
            newQuery = query #jek: instead of tag2symbol
        else:
            idx1 = 0
            for i in range(len(query)):
                if query[i] == '(' or query[i] == ')' or query[i] == ' ':
                    if idx1 != i:
                        '''jekif query[idx1:i] not in tag2symbol:
                            return []
                        tagsymbol = tag2symbol[query[idx1:i]]
                        newQuery = newQuery + tagsymbol'''
                        newQuery = newQuery + query[idx1:i] #jek:intead of symbol
                    newQuery = newQuery + query[i]
                    idx1 = i + 1
        #newQuery = newQuery.replace(' ', '') #
        if newQuery not in self.indexMap:
            return []
        syntaxInfoList = self.indexMap[newQuery]
        results = []

        # 어절 개수가 2개 이상인 경우를 원할 때
        if minWordCount > 1:
            # 색인은 어절개수의 오름차순으로 정렬되어 있고
            # minIdx 번째 부터 어절개수가 minwordCount개 이상이다.
            minIdx = syntaxInfoList.minWordCountIdx(minWordCount)
            # minWordCount 보다 어절 개수가 많은 결과가 없는 경우
            # 빈 리스트 반환
            if minIdx == -1:
                return []
            else:
                start = start + syntaxInfoList.minWordCountIdx(minWordCount)

        for i in range(start, start+count):
            if i == syntaxInfoList.length():
                break
            syntaxInfo = SyntaxInfo('', syntaxInfoList.sentenceIds[i],
                            syntaxInfoList.startIdxs[i],
                            syntaxInfoList.endIdxs[i],
                            syntaxInfoList.openPIdxs[i],
                            syntaxInfoList.closePIdxs[i], 0)
            sentence = self.sentenceStorage[syntaxInfo.sentenceId]
            # 매칭된 구문정보 부분에 하일라이팅 처리
            # startIdx번째 어절의 openPIdx번째 여는 괄호부터
            # endIdx번째 어절의 closePIdx번째 닫는 괄호
            # 0번째 라인은 문장
            # 1번째 라인부터가 구문 구조, 즉 1번째 라인이 0번째 어절에 대한 정보
            splits = sentence.split('\n')
            # 하일라이팅. 단, 문장 맨앞의 '; ' 부분은 자른다.
            newSentence = '%s\n' % highlightSentence(splits[0][2:], syntaxInfo.startIdx, syntaxInfo.endIdx)
            for j in range(1, len(splits)):
                if j-1 == syntaxInfo.startIdx:
                    pos = -1
                    for k in range(syntaxInfo.openPIdx+1):
                        pos = splits[j].find('(', pos+1)
                    splits[j] = '%s<!START>%s' % (splits[j][:pos], splits[j][pos:])
                if j-1 == syntaxInfo.endIdx:
                    pos = -1
                    for k in range(syntaxInfo.closePIdx+1):
                        pos = splits[j].find(')', pos+1)
                    splits[j] = '%s<!END>%s' % (splits[j][:pos+1], splits[j][pos+1:])
                newSentence = newSentence + splits[j] + '\n'
            # '; ' 다시 붙인다.
            newSentence = '; ' + newSentence.rstrip()
            results.append((syntaxInfo, newSentence))

        return results


if __name__ == "__main__":
    try:
        import pdb
        sch = Searcher('../')
        rst = sch.search('NP(NP NP)', 0, 100)
        print(rst)
    except Exception as e:
        print(e)
