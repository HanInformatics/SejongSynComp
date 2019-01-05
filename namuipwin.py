#-*- coding: utf-8 -*-
# writer: jek.cl.nlp@gmail.com
# updated date: 2018/09, python3.X

from tkinter import *
import Pmw
from tkinter import filedialog #python3
import pdb
import namuip
from namuip import *

class Shell:
    def __init__(self, namuip, title=''):
        self.root = Tk()
        self.root.geometry("%dx%d" % (800,600))
        self.root.option_add('*font', ('verdana', 11, 'bold'))
#        Pmw.initialise(self.root)
        self.root.title(title)
        self.searcher = namuip
        self.indexer = namuip
        self.compressor = namuip
        self.searchrst     = {} # for save
        self.indexFlag = 0
        self.cursor = 0

    def doBaseForm(self, master):
        self.balloon = Pmw.Balloon(master)
        self.doMenuBar(master)
        # input query
        self.queryFrame = Frame(master)
        self.queryFrame.pack(fill='x', expand=0)
        self.doQueryForm()
        self.doButtonForm()

        # concordance result
        self.concFrame = Frame(master)
        self.concFrame.pack(fill='both', expand=1, padx = 10)
        shell.doConcForm()

        # Add balloon text to statusBar
        self.statusBar = Pmw.MessageBar(master, entry_width = 40,
                                        entry_relief='groove',
                                        labelpos = 'w',
                                        label_text = '')
        self.statusBar.pack(fill = 'both', padx = 10, pady = 10)
        self.balloon.configure(statuscommand = self.statusBar.helpmessage)

    def doMenuBar(self, master):
        self.menuBar = Pmw.MenuBar(master, hull_borderwidth=1,
                              hull_relief = 'raised',
                              hotkeys=1, balloon = self.balloon)
        self.menuBar.pack(fill='x')
        self.menuBar.addmenu('Search', 'Search')
        self.menuBar.addmenuitem('Search', 'command', 'Get search result',
                                label='Get result', command=self.doDisplay)
        self.menuBar.addmenu('Search & Compress', 'Search & Compress')
        self.menuBar.addmenuitem('Search & Compress', 'command', 'Get search&compress result',
                                label='Get result', command=self.doDisplay2)
        self.menuBar.addmenu('Save', 'Save')
        self.menuBar.addmenuitem('Save', 'command', 'Save search result',
                                label='Save result', command=self.saveRst)
        self.menuBar.addmenu('Indexing', 'Indexing')
        self.menuBar.addmenuitem('Indexing', 'command', 'Indexing the data',
                                label='Indexing', command=self.indexData)
        self.menuBar.addmenu('Help', 'Help')
        self.menuBar.addmenuitem('Help', 'command', 'Get information on application',
                                    label='About...', command=self.help)
        self.menuBar.addmenu('Exit', 'Exit')
        self.menuBar.addmenuitem('Exit', 'command', 'Exit the application',
                                label='Exit', command=self.root.destroy)

        # Create about dialog.
        Pmw.aboutversion('0.2')
        Pmw.aboutcontact('\nFor information about this application contact:\n\n' +
                    'email:jek.cl.nlp@gmail.com, \n sragent@gmail.com \n'
                    '\'21세기 세종 구문분석 말뭉치\' 용례 추출& 문장 압축기\n'
                    )
        self.about = Pmw.AboutDialog(master,
                                     applicationname = '나무-잎')
        self.about.withdraw()

    def doExample(self):
        self.cleardisplay()
        file = open('query.txt')
        displayquery = ''
        for line in file.readlines():
            line = line.strip()
            displayquery = displayquery + line + '; '
            self.query.setentry(displayquery)
            self.doDisplay(0)
        file.close()

    def saveRst(self):
        ofile = asksaveasfilename(filetypes=[("txt file", "txt"),("All files", "*")])
        if ofile:
            self.currentName = ofile
            self.doSave()

    def doSave(self):
        fd = open(self.currentName, 'w')
        self.cleardisplay()
        self.board.insert(END, "save...\n")
        for key in self.searchrst.keys():
            fd.write("%s\n" %self.searchrst[key])
        fd.close()
        self.board.insert(END, "done...\n")

    def indexData(self):
        self.board.insert(END, 'Indexing starts...\n')
        # 'are you sure?'
        self.indexer.Storage.build('./syn_utf8', 'storage.data')
        ret = self.indexer.Indexer.build('storage.data', 'index.data')
        if ret != 0 :
            self.board.insert(END, "indexing fail\nSo, you may have problem in search\nSee 'Help'\n")
        self.board.insert(END, 'indexing done\n')

    def doNext(self):
        self.doDisplay(1)

    def doPre(self):
        self.doDisplay(-1)

    def doDisplay(self, page = 0):
        self.cleardisplay()
        if page == 0 :
            self.cursor = 0
        elif page == -1 and self.cursor > 199 :
            self.cursor -= 200
        elif page == 1 and self.cursor > 1 :
            pass
        else :
            self.cursor = 0
        try :
            query = self.query.get()
            results = self.searcher.search(query.strip(), self.cursor, 100)

            lenOfrst = len(results)
            if lenOfrst >= 1 :
                self.board.insert(END, '(%d ~ %d)\n\n' %(self.cursor+1, (self.cursor+lenOfrst)), 'bold')
                self.cursor += lenOfrst
                iLine = 0
                #self.board.insert(END, '\n========================\n', 'highlight')
                #self.board.insert(END, '%s ' %(query), 'highlight')
                for info, sentence in results:
                    iLine += 1
                    self.searchrst[info.sentenceId] = sentence
                    lines = sentence.split('\n')
                    lighterflag = 0
                    for line in lines:
                        if line[0:2] =='; ' :
                            self.printSrc(line, iLine)
                            continue
                        pos_s = line.find('<!START>')
                        pos_e = line.find('<!END>')
                        if pos_s != -1 : lighterflag = 1
                        if lighterflag == 1 :
                            if pos_s != -1 :
                                if pos_e == -1 :
                                    self.board.insert(END, '%s' %line[:pos_s], 'backlighter')
                                    self.board.insert(END, '%s\n' %line[pos_s+8:], ('highlight','backlighter'))
                                else:
                                    self.board.insert(END, '%s' %line[:pos_s], 'backlighter')
                                    self.board.insert(END, '%s' %line[pos_s+8:pos_e], ('highlight','backlighter'))
                                    self.board.insert(END, '%s\n' %line[pos_e+6:],'backlighter' )
                                    lighterflag = 0
                                    continue
                            else :
                                if pos_e != -1 :
                                    self.board.insert(END, '%s' %line[:pos_e], ('highlight','backlighter'))
                                    self.board.insert(END, '%s\n' %line[pos_e+6:],'backlighter' )
                                    lighterflag = 0
                                else:
                                    self.board.insert(END, '%s\n' %line, ('highlight','backlighter'))
                                continue
                        else :
                            self.board.insert(END, '%s\n' %line)
                    self.board.insert(END, '\n')
            else :
                 self.board.insert(END, '더 이상 결과가 없습니다\n')
        except Exception as e:
            self.board.insert(END, 'No result : %s\n' %e)


    def doDisplay2(self, page = 0): #for compression
        self.cleardisplay()
        if page == 0 :
            self.cursor = 0
        elif page == -1 and self.cursor > 199 :
            self.cursor -= 200
        elif page == 1 and self.cursor > 1 :
            pass
        else :
            self.cursor = 0
        try :
            query   = self.query.get()
            results = self.searcher.search(query.strip(), self.cursor, 100)
            com_results = self.compressor.compress_list(results)

            lenOfrst = len(com_results)
            if lenOfrst >= 1 :
                self.board.insert(END, '(%d ~ %d)\n\n' %(self.cursor+1, (self.cursor+lenOfrst)), 'bold')
                self.cursor += lenOfrst
                iLine = 0
#                self.board.insert(END, '\n========================\n', 'highlight')
                #self.board.insert(END, '%s ' %(query), 'highlight')
                for info, sentence in com_results:
                    iLine += 1
                    self.searchrst[info.sentenceId] = sentence
                    lines = sentence.split('\n')
                    lighterflag = 0
                    for line in lines:
                        if line[0:2] =='; ' :
                            self.printSrc(line, iLine)
                            continue
                        pos_s = line.find('<!START>')
                        pos_e = line.find('<!END>')
                        if pos_s != -1 : lighterflag = 1
                        if lighterflag == 1 :
                            if pos_s != -1 :
                                if pos_e == -1 :
                                    self.board.insert(END, '%s' %line[:pos_s], 'backlighter')
                                    #self.board.insert(END, '%s\n' %line[pos_s+8:], ('highlight','backlighter'))
                                    sub_line = ' '*(len(line[pos_s+8:]))
                                    self.board.insert(END, '%s\n' %sub_line, ('highlight','backlighter'))
                                else:
                                    self.board.insert(END, '%s' %line[:pos_s], 'backlighter')
                                    #self.board.insert(END, '%s' %line[pos_s+8:pos_e], ('highlight','backlighter'))
                                    sub_line = ' '*(len(line[pos_s+8:pos_e]))
                                    self.board.insert(END, '%s' %sub_line, ('highlight','backlighter'))
                                    self.board.insert(END, '%s\n' %line[pos_e+6:],'backlighter' )
                                    lighterflag = 0
                                    continue
                            else :
                                if pos_e != -1 :
                                    #self.board.insert(END, '%s' %line[:pos_e], ('highlight','backlighter'))
                                    sub_line = ' '*(len(line[:pos_e]))
                                    self.board.insert(END, '%s' %sub_line, ('highlight','backlighter'))
                                    self.board.insert(END, '%s\n' %line[pos_e+6:],'backlighter' )
                                    lighterflag = 0
                                else:
                                    self.board.insert(END, '%s\n' %line, ('highlight','backlighter'))
                                continue
                        else :
                            self.board.insert(END, '%s\n' %line)
                    self.board.insert(END, '\n')
            else :
                 self.board.insert(END, '더 이상 결과가 없습니다\n')
        except Exception as e:
            self.board.insert(END, 'No result : %s\n' %e)

    def printSrc(self, line, num):
        line = line[2:]
        pos_s = line.find('<!START>')
        pos_e = line.find('<!END>')
        if pos_s != -1 and pos_e != -1 :
            self.board.insert(END, '[%s] ' %str(num))
            self.board.insert(END, '%s' %line[:pos_s], 'nlbold')
            self.board.insert(END, '%s' %line[pos_s+8:pos_e], ('nlhighlight'))
            self.board.insert(END, '%s\n' %line[pos_e+6:],'nlbold' )
        else :
            print('fail in src line\n')
            pass

    def help(self):
        self.about.show()

    def doQueryForm(self):
        self.query = Pmw.EntryField(self.queryFrame, entry_width=40,
                                       value='NP(VP NP(NP NP))',
                                       modifiedcommand=self.update_query,
                                       command = self.doDisplay,
                                       label_text='Query : ',
                                       labelpos=W, labelmargin=1)
        self.query.component('entry').focus_set()
        self.query.pack(side='left', expand=0, padx=5, pady=8)

    def doButtonForm(self):
        self.search_btn = Button(self.queryFrame, text='Search', command=self.doDisplay)
        self.search_btn.pack(side ='left', expand=0, padx=5, pady=8)
        #self.search_comp_btn = Button(self.queryFrame, text='Search & Compress', command=self.doDisplay2)
        self.search_btn = Button(self.queryFrame, text='Search & Compress', command=self.doDisplay)
        #self.search_comp_btn.pack(side ='left', expand=0, padx=5, pady=8)
        self.next_btn = Button(self.queryFrame, text='Next', command=self.doNext)
        self.next_btn.pack(side = 'left', expand=0, padx=5, pady=8)
        self.pre_btn = Button(self.queryFrame, text='Prev', command=self.doPre)
        self.pre_btn.pack(side ='left', expand=0, padx=5, pady=8)

    def doConcForm(self):
        self.board = Pmw.ScrolledText(self.concFrame,
                                         borderframe = 1,
                                         labelpos = 'n',
                                         usehullsize = 1,
                                         hull_width = 270,
                                         hull_height = 600,
                                         text_padx = 10,
                                         text_pady = 10,
                                         text_wrap='none')
        self.board.configure(text_font = ('verdana', 9))
        self.board.pack(fill = 'both', expand = 1)
        self.board.tag_configure('backlighter', background='yellow')
        self.board.tag_configure('highlight', font=('Verdana', 10, 'bold', 'italic'), foreground='brown')
        self.board.tag_configure('nlbold', font=('Verdana', 10, 'bold'), foreground='black')
        self.board.tag_configure('nlhighlight', font=('Verdana', 10, 'bold'), foreground='brown')

    def update_query(self):
        query = self.query.get().upper()
        if query:
            self.query.setentry(query)

    def cleardisplay(self) :
        self.board.component('text').delete(1.0, END)

    # loading
    def loadData(self):
        try :
            self.searcher = self.searcher.Searcher('./')
            self.board.insert(END, 'data loading done\n')
            self.board.insert(END, '=================================================\n')
            self.board.insert(END, 'query example : \n')
            self.board.insert(END, '     NP(VP_MOD NP)\n')
            self.board.insert(END, '     np(np np(np_cnj np))\n')
            self.board.insert(END, '=================================================\n')
            self.compressor = self.compressor.Compressor('./')
        except Exception as e:
            self.board.insert(END, 'loading fail\n')


if __name__ == '__main__':
    titlename = '나무-잎(namu-ip)'
    shell=Shell(namuip, title=titlename)
    shell.doBaseForm(shell.root)
    shell.loadData() # if you just show front ui, this line should be blocked
    shell.root.mainloop()


