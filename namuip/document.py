# -*- coding: utf-8 -*-
# 작성자 : 심보준(sragent@gmail.com)
'''2018.02. by jek
index from utf16 to utf-8
change storage data of c-struct binary to naive texts
add unit test
remove & comment regacy codes based on Python3.xx
'''

import os
import codecs
import struct
import array

class Storage:
    """ '나무-잎' 패키지 저장소 클래스
    말뭉치 본문을 저장하고 탐색한다. """
    @staticmethod
    def build(dirName, outputFileName):
        """ dir 디렉토리에 있는 텍스트 파일을 읽어서 문장 단위로 분리 후
        sentence_id로 직접 access가 가능한 저장소 자료구조로 만든 후 파일로 저장한다. """
        print('저장소(storage) 생성 시작')
        corpusFiles = os.listdir(dirName)
        sentences = []
        for corpusFile in corpusFiles:
            if not corpusFile.endswith('.txt'):
                continue
            corpusFile = dirName + '/' + corpusFile
            sentences = sentences + Storage.__extractSentences(corpusFile)
            print('%s done' % corpusFile)
        print('저장소 생성 완료 : %d 문장' % len(sentences))
        Storage.__writeToFile(sentences, outputFileName)

    @staticmethod
    def __extractSentences(fileName):
        """ 말뭉치 파일에서 문장 부분을 문장 배열에 담아서 리턴
        build 메소드에서 호출한다. """
        # 세종 구문분석 말뭉치는 utf-16인코딩
        #jek:files are converted in utf8 and saved in syn_utf8
        fp = codecs.open(fileName, encoding='utf-8') #jek.
        sentence = ''
        sentences = []
        setStart = False
        for line in fp:
            #jekline = line.encode('utf-8').rstrip()
            line = line.rstrip() #jek.
            if line.strip() == '<body>':
                setStart = True
                continue
            if line.strip() == '</body>':
                break
            if not setStart:
                continue
            # 문장의 시작
            if line.startswith('; ') and sentence != '':
                sentences.append(sentence.rstrip())
                sentence = ''
            sentence = sentence + line + '\n'

        sentences.append(sentence.rstrip())
        return sentences

    @staticmethod
    def __writeToFile(sentences, outputFileName):
        #jek
        outfile = open(outputFileName, 'w')
        for sentence in sentences:
            outfile.write('%s\n' %sentence)
        outfile.close()
        return
        #jek end
        """ sentences list를 binary storage 파일로 만든다.
        build 메소드에서 호출한다. """
        lengths = array.array('i')
        #jeksentenceData = array.array('c')
        sentenceData = array.array('u') #jek:index.py:155
        #https://docs.python.org/2/library/array.html
        #jek:https://www.programiz.com/python-programming/array, https://stackoverflow.com/questions/37142319/array-of-characters-in-python-3
        #2018.12.23, array item must be unicode character
        totalLength = 0
        for sentence in sentences:
            lengths.append(len(sentence))
            sentenceData.extend(sentence)
            totalLength = totalLength + len(sentence)

        wfp = open(outputFileName, 'wb')
        data = struct.pack('i', len(sentences))
        wfp.write(data)
        data = struct.pack('l', totalLength)
        wfp.write(data)
        lengths.tofile(wfp)
        sentenceData.tofile(wfp)
        wfp.close()

    def __init__(self):
        self.sentences = []

    def load(self, fileName):
        #jek
        infile = open(fileName, encoding='utf-8')
        lines = infile.readlines()
        infile.close()
        parsed = ''
        for line in lines:
            if line[0] == ';' and len(parsed)>0:
                self.sentences.append(parsed)
                parsed = ''
            parsed = parsed + line

        self.sentences.append(parsed)
        return self.sentences
        #jek end

        """ 저장소 파일을 메모리에 적재한다. """
        rfp = open(fileName, 'rb')
        count, = struct.unpack('i', rfp.read(struct.calcsize('i')))
        totalLength, = struct.unpack('l', rfp.read(struct.calcsize('l')))

        lengths = array.array('i')
        #jeksentenceData = array.array('c')
        sentenceData = array.array('u')
        lengths.fromfile(rfp, count)
        sentenceData.fromfile(rfp, totalLength)

        sentenceStart = 0
        for i in range(count):
            sentence = sentenceData[sentenceStart:sentenceStart+lengths[i]].tostring()
            self.sentences.append(sentence)
            #print('storage:', sentence) #jek bytes
            sentenceStart = sentenceStart + lengths[i]

    def __getitem__(self, idx):
        """ sentence id로 용례 문장을 직접 access 한다. """
        return self.sentences[idx]

#jek
if __name__ == "__main__":
    try :
        import pdb
        pdb.set_trace()
        docs = Storage()
        docs.build('../syn_utf8', 'storage.data')
        sens = docs.load('storage.data')
    except Exception as e:
        print(e)

