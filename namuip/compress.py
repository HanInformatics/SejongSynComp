# -*- coding: utf-8 -*-
# 작성자 : 조은경 (jek.cl.nlp@gmail.com)

from namuip.common import *
import struct
import array
import sys

class Compressor:
    """ '나무-잎' 패키지 압축기 클래스
    Searcher에서 가져온 문장을 축약 규칙에 의해 구조를 줄인다."""

    def __init__(self, homeDir):
        """ 규칙 파일을 메모리에 적재한다.
        """
        print(utf8Line('축약기 동작 시작'))
        self.searcher = None
        self.compRules = None
        self.__loadRules(homeDir + '/comp.rules')
        print(utf8Line('\n축약 규칙 적재 완료'))

    def __loadRules(self, srcfilename):
        self.compRules = {}
        infile = open(srcfilename)
        for l in infile.readlines():
            l = l.strip()
            if l == '' or (len(l)>0 and l[0]=='#') : continue
            src_dst = l.split('\t')
            self.compRules[src_dst[0]] = src_dst[1]
        infile.close()
        #print self.compRules
        print('%s is loaded' %(srcfilename))
        return

    def compress(self, sentence_org, comp_opt=1):
        """
        sentence_org :
        comp_opt : level of compressing
        """
        results = sentence_org
        return results

    def compress_list(self, sentences_org, comp_opt=1):
        """
        sentence_org :
        comp_opt : level of compressing
        """
        print(__name__)
        for sent in sentences_org :
            syn_info = sent[0]
            sen_string = sent[1]
            #print(sent[1].decode('utf-8').encode('utf-8'))
        return sentences_org #results

    @classmethod
    def copy_src_dst(cls, srcfilename, outfilename):
        infile = open(srcfilename)
        outfile = open(outfilename, 'w')
        for l in infile.xreadlines():
            l = l.strip()
            if l == '' : continue
            outfile.write('%s\t%s\n' %(l, l))
        outfile.close()
        infile.close()

if __name__ == "__main__":
    try :
        test = Compressor('../')
        test.compress_list([('qq', 1), ('bb', 2)])
        #Compressor.copy_src_dst(sys.argv[1], sys.argv[2])
        #test.copy_src_dst(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(e)
