# -*- coding: utf-8 -*-
# 작성자 : 심보준(sragent@gmail.com)
''' 추가 : 은경 2017.02.
add 'wstring' for checking word itself
add unit test to the very last line
'''

from document import Storage
from common import *
import sys
import struct
import array

g_file = open('phrases.txt', 'w')

class ParseTreeNode:
    """구문 구조 용례를 파싱하기 위해서는 먼저 Tree 구조를 building하는데 이때 쓰이는 노드 클래스
    멤버 변수는 SyntaxInfo와 동일한 정보에 노드를 구성하고 이동하는 데에 필요한 링크 정보들이 있다.

    tag -- 구문구조 태그 정보 예) NP(VP NP)
    sentenceId -- 구문 구조가 발견된 문장의 id, 구문분석 말뭉치의 문장에 각각 할당한 일련번호
    startIdx -- 구문 구조 정보가 시작되는 어절의 인덱스 - 하일라이팅에 이용
    endIdx -- 구문 구조 정보가 끝나는 어절의 인덱스 - 하일라이팅에 이용
    openPIdx -- startIdx 어절에서 구문구조 정보가 몇번째 여는 괄호에서 시작되는가? - 하일라이팅에 이용
    closePIdx -- endIdx 어절에서 구문구조 정보가 몇번째 닫는 괄호에서 끝나는가? - 하일라이팅에 이용
    parent -- 부모 노드
    left -- 왼쪽 자식 노드
    right -- 오른쪽 자식 노드

    root 노드는 오른쪽 자식 노드만 None 이고, leaf노드는 양쪽 자식노드가 모두 None이다. """
    def __init__(self):
        self.tag = ''
        self.startIdx = -1
        self.endIdx = -1
        self.openPIdx = -1
        self.closePIdx = -1
        self.left = None
        self.right = None
        self.parent = None
        self.wstring = None

    def printTree(self, level):
        indent = ''
        for i in xrange(level):
            indent = indent + '\t'
        print '%s[' % indent
        if self.tag in symbol2tag:
            t = symbol2tag[self.tag]
        else:
            t = self.tag
        print '%stag : %s' % (indent, t)
        print '%sstart : %d' % (indent, self.startIdx)
        print '%send : %d ' % (indent, self.endIdx)
        if self.left != None:
            print '%sleft node' % indent
            self.left.printTree(level + 1)
        if self.right != None:
            print '%sright node' % indent
            self.right.printTree(level + 1)
        print '%s]' % indent

class Indexer:
    """ '나무-잎' 패키지 색인기 클래스
    태그정보 key --> SyntaxInfoList 형태의 역색인을 만든다.
    Storage 파일을 입력으로, 저장소 안의 모든 구문구조 용례를 분석하여 색인을 만든다.

    1. __buildParseTree -- 구문 구조 용례 문장에서 ParseTree를 구성한다.
    2. __thrashTree -- ParseTree를 recursive하게 순회하면서 SyntaxInfo 들을 추출한다.
    3. build -- 에서 각 문장 구문 구조마다 buildParseTree thraseTree를 반복하면서 indexMap을 builing한다.
    4. __sortSyntaxInfoList -- indexMap의 각 SyntaxInfoList들을 어절 개수의 오름차순으로 정렬한다.
        최소 개 이상인 구문구조를 검색 가능하게 하기 위해서이다.
    5. __writeToFile -- 파일로 저장한다."""
    # 태그 정보를 생성하는 태그 개수에 제한을 둔다.
    MAX_TAG_COUNT = 10

    @staticmethod
    def build(storageFileName, outputFileName):
        """ storagefile에 저장된 구문구조 용례를 읽어들여 색인을 만들고 파일로 저장한다. """
        print utf8Line('\n색인 시작')
        sentences = Storage()
        sentences.load(storageFileName)
        sentenceId = 0
        indexMap = {}
        for sentence in sentences:
            # 문장마다 syntax 정보를 읽어들여서
            #pdb.set_trace()
            syntaxInfos = Indexer.__getSyntaxInfos(sentence)
            for syntaxInfo in syntaxInfos:
                syntaxInfo.sentenceId = sentenceId
                key = syntaxInfo.info
                if key not in indexMap:
                    indexMap[key] = SyntaxInfoList()
                # 읽어들인 syntax 정보를 indexMap에 저장한다.
                indexMap[key].addSyntaxInfo1(syntaxInfo)
            sentenceId = sentenceId + 1
            if sentenceId % 1000 == 0:
                sys.stdout.write('[%d]' % sentenceId)
                sys.stdout.flush()
        # 각 syntaxList를 어절개수의 오름차순으로 정렬한다.
        print utf8Line('\n구문 구조 정보 정렬중')
        for key, syntaxInfoList in indexMap.iteritems():
            indexMap[key] = Indexer.__sortSyntaxInfoList(syntaxInfoList)
        # 파일로 저장
        Indexer.__writeToFile(indexMap, outputFileName)
        print utf8Line('색인 완료')
        print syntaxInfoList.printList() #XXX:TODO

        return 0

    @staticmethod
    def __sortSyntaxInfoList(syntaxInfoList):
        """indexMap의 각 SyntaxInfoList들을 오름차순으로 정렬한다.
        최소 개 이상인 구문구조 정보를 검색 가능하게 하기 위해서이다.

        파이썬의 내장 sort함수를 이용하기 위해서
        SyntaxInfoList를 SyntaxInfo의 배열로 옮겨서 정렬하고 다시 옮긴다. """
        syntaxInfoArray = []
        for i in xrange(syntaxInfoList.length()):
            syntaxInfo = SyntaxInfo('', syntaxInfoList.sentenceIds[i],
                            syntaxInfoList.startIdxs[i],
                            syntaxInfoList.endIdxs[i],
                            syntaxInfoList.openPIdxs[i],
                            syntaxInfoList.closePIdxs[i], 0)
            syntaxInfoArray.append(syntaxInfo)

        syntaxInfoArray.sort()
        newSyntaxInfoList = SyntaxInfoList()
        for syntaxInfo in syntaxInfoArray:
            newSyntaxInfoList.addSyntaxInfo1(syntaxInfo)
        return newSyntaxInfoList

    @staticmethod
    def __writeToFile(indexMap, outputFileName):
        """ 색인을 파일로 저장한다.
        Searcher의 __loadIndex 함수와 호환되어야 한다. """
        print utf8Line('색인 정보를 파일로 저장중')

        # 저장할 변수와 배열들

        # key 문자열의 길이의 총합
        # key 문자열을 한꺼번에 읽기 위해 필요
        totKeyLength = 0
        # key 한개에 여러개의 구문정보가 들어간다.
        # 구문정보 개수의 총합
        # 구문정보를 한꺼번에 읽기 위해 필요
        totSyntaxInfoCount = 0
        # 각 key마다 key길이
        keyLengthArray = array.array('i')
        # 모든 key를 붙여서 하나의 정보로 저장
        keyCharArray = array.array('c')
        # 각 key마다 구문정보 개수
        syntaxInfoCountArray = array.array('i')
        # 모든 구문정보를 한번에 저장
        syntaxInfoArray = array.array('i')

        # 정보를 위 변수와 배열에 담는다.
        for key, syntaxInfoList in indexMap.iteritems():
            keyLength = len(key)
            totKeyLength = totKeyLength + keyLength
            keyLengthArray.append(keyLength)
            keyCharArray.extend(key)
            totSyntaxInfoCount = totSyntaxInfoCount + syntaxInfoList.length()
            syntaxInfoCountArray.append(syntaxInfoList.length())
            for i in xrange(syntaxInfoList.length()):
                syntaxInfoArray.append(syntaxInfoList.sentenceIds[i])
                syntaxInfoArray.append(syntaxInfoList.startIdxs[i])
                syntaxInfoArray.append(syntaxInfoList.endIdxs[i])
                syntaxInfoArray.append(syntaxInfoList.openPIdxs[i])
                syntaxInfoArray.append(syntaxInfoList.closePIdxs[i])

        # 변수와 배열들을 파일에 쓴다.
        wfp = open(outputFileName, 'wb')
        # key 개수
        data = struct.pack('i', len(indexMap))
        wfp.write(data)
        data = struct.pack('l', totKeyLength)
        wfp.write(data)
        data = struct.pack('l', totSyntaxInfoCount)
        wfp.write(data)
        keyLengthArray.tofile(wfp)
        keyCharArray.tofile(wfp)
        syntaxInfoCountArray.tofile(wfp)
        syntaxInfoArray.tofile(wfp)
        wfp.close()

    @staticmethod
    def __getSyntaxInfos(sentence):
        """구문 구조 용례 문장을 받아서 SyntaxInfo 리스트를 반환한다. """
        # 첫줄은 문장이고, 그 다음줄 부터('\n'+1) 구문구조이다.
        parseTree = Indexer.__buildParseTree(sentence[sentence.find('\n')+1:]) #convert tag to symbol
        syntaxInfos = []
        Indexer.__thrashTree(parseTree, syntaxInfos)
        #맨끝 정보는 root 노드 정보라서 제거
        syntaxInfos.pop()
        return syntaxInfos

    @staticmethod
    def __thrashTree(parseTree, syntaxInfos):
        """ ParseTree를 recursive하게 순회하면서 SyntaxInfo 들을 추출한다.
        최초 호출되는 parseTree는 root node """
        leftSyntaxInfos = rightSyntaxInfos = None
        localSyntaxInfos = []
        if parseTree.left != None:
            leftSyntaxInfos = Indexer.__thrashTree(parseTree.left, syntaxInfos)

        if parseTree.right != None:
            rightSyntaxInfos = Indexer.__thrashTree(parseTree.right, syntaxInfos)

        curNodeSyntaxInfo = SyntaxInfo(parseTree.tag, -1, parseTree.startIdx,
                            parseTree.endIdx, parseTree.openPIdx, parseTree.closePIdx, 1)
        localSyntaxInfos.append(curNodeSyntaxInfo)

        if leftSyntaxInfos == None or rightSyntaxInfos == None:
            syntaxInfos.extend(localSyntaxInfos)
            return localSyntaxInfos

        for leftSyntaxInfo in leftSyntaxInfos:
            for rightSyntaxInfo in rightSyntaxInfos:
                if leftSyntaxInfo.tagCount + rightSyntaxInfo.tagCount + 1> Indexer.MAX_TAG_COUNT:
                    #print 'max_tag_count', leftSyntaxInfo.info , rightSyntaxInfo.info
                    continue
                #XXXsubSyntaxInfo = SyntaxInfo(parseTree.tag + '(' + leftSyntaxInfo.info + rightSyntaxInfo.info + ')',
                subSyntaxInfo = SyntaxInfo(parseTree.tag + '(' + leftSyntaxInfo.info +' '+ rightSyntaxInfo.info + ')',
                                    -1, leftSyntaxInfo.startIdx, rightSyntaxInfo.endIdx,
                                    parseTree.openPIdx, parseTree.closePIdx,
                                    leftSyntaxInfo.tagCount+rightSyntaxInfo.tagCount+1)
                localSyntaxInfos.append(subSyntaxInfo)

        syntaxInfos.extend(localSyntaxInfos)
        return localSyntaxInfos

    @staticmethod
    def __buildParseTree(egSentence):
        """구문 구조 용례 문장에서 ParseTree를 구성한다. """
        rootNode = ParseTreeNode()
        curNode = rootNode
        egLines = egSentence.split('\n')

        for lineNum in xrange(len(egLines)):
            egLine = egLines[lineNum]
            i = -1
            # 하일라이팅을 위해서 몇번째 왼쪽 괄호인지, 오른쪽 괄호인지를 저장한다.
            openPIdx = 0
            closePIdx = 0
            # 여는 태그 '('가 나오면 노드를 하나씩 만들고
            # 닫는 태그 ')'가 나오면 부모 노드로 하나씩 거슬러 올라간다.
            while(i+1 < len(egLine)):
                i = i + 1
                # 실제 문장에서 '(' 나 ')'가 나오는 경우 /SS가 따라 나온다.
                if egLine[i] == '(' and i+1 < len(egLine) and egLine[i+1] != '/':
                    if curNode.left == None:
                        curNode.left = ParseTreeNode()
                        curNode.left.parent = curNode
                        curNode = curNode.left
                    elif curNode.right == None:
                        curNode.right = ParseTreeNode()
                        curNode.right.parent = curNode
                        curNode = curNode.right
                    else:
                        print 'syntax error type2! : %s' % egLine
                    tagEndIdx = egLine.find(' ', i+1)
                    tagEndIdx2 = egLine.find(';', i+1)
                    if tagEndIdx2 != -1 and tagEndIdx2 < tagEndIdx:
                        tagEndIdx = tagEndIdx2
                        #--raw_input("left %s, i:%d" %(egLine[tagEndIdx+1:], i))
                    tag = egLine[i+1:tagEndIdx]
                    '''jek
                    if tag not in tag2symbol:
                        # 의미 없는 태그 문자로 대체
                        print >> sys.stderr, 'ztag:', tag #, egLine #XXX
                        curNode.tag = 'z'
                    else:
                        curNode.tag = tag2symbol[tag]
                    jek'''
                    curNode.tag = tag #XXX instead of jek.

                    #raw_input("left %s, %s, i:%d" %(tag, egLine[i+1:], i))
                    curNode.startIdx = lineNum
                    curNode.openPIdx = openPIdx
                    openPIdx = openPIdx + 1
                    #raw_input("left tag, %s,  %s, i:%d" %(tag, egLine[tagEndIdx+1:], i))
                    curNode.wstring = tag #XXX

                elif egLine[i] == ')' and (i == len(egLine)-1 or egLine[i+1] != '/'):
                    curNode.endIdx = lineNum
                    curNode.closePIdx = closePIdx
                    closePIdx = closePIdx + 1
                    curNode = curNode.parent
                    if egLine[i-1] != ')' :
                        #raw_input("right %s, i:%d" %(egLine[tagEndIdx+1:i], i))
                        curNode.wstring = egLine[tagEndIdx+1:] #XXX

                if curNode == rootNode:
                    break
        return rootNode


if __name__ == "__main__":
    try :
        test = Indexer()
        import pdb
        #pdb.set_trace()
        test.build('../storage.data', 'unit.index.data')

    except Exception, e:
        print e

