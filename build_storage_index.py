#-*-coding:utf-8 -*-

import namuip
import pdb

if __name__ == '__main__':
    namuip.Storage.build('./syn_utf8', 'storage.data')
    #pdb.set_trace()
    namuip.Indexer.build('storage.data', 'index.data')
