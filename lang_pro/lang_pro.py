#coding: utf-8
import sys, CaboCha, re, random

class Morph:
    #形態素クラス:表層形(surface),基本形(base),品詞(pos),品詞細分類1(pos1)
    def __init__(self, surface, base, pos, pos1):
        self.surface = surface
        self.base = base
        self.pos = pos
        self.pos1 = pos1

class Chunk:
    #文節クラス:形態素のリスト（morphs）,係り先文節インデックス番号（dst）,係り元文節インデックス番号のリスト（srcs）
    def __init__(self):
        self.morphs = []
        self.srcs = []
        self.dst = -1
    def normalized_surface(self):
        result = ''
        for morph in self.morphs:
            result += morph.surface
        return result
    def get_pos(self, pos):
        #引数:品詞 返り値:文節中に含まれる指定した品詞の表層形のリスト
        return [morph.surface for morph in self.morphs
                    if morph.pos == pos]
    def replace_pos(self, pos, fname):
        """
        引数:品詞,ファイル名
        返り値:文節中に含まれる指定した品詞を持つ単語を指定したファイルの中からランダムに一つ選んだ単語と置換して再構成される文字列
        """
        result = ''
        for morph in self.morphs:
            if morph.pos == pos:
                result += "".join(random.sample(open(fname,"r", encoding='utf-8').readlines(),1))[:-1]
            else:
                result += morph.surface
        return result

class lang_pro:
    path = {'app_lib' : '../../account/'+sys.argv[1]+'/lib/lang_pro'}
    f_list = {
        't_list' : path['app_lib']+'/tweet_list.txt',
        't_parsed' : path['app_lib']+'/tweet_list.txt.cabocha',
        't_lib' : path['app_lib']+'/tweet_lib.txt',
        'target_parsed' : path['app_lib']+'/target.txt.cabocha',
        'containts' : path['app_lib']+'/tweet_containts.txt'
    }
    cabocha = CaboCha.Parser()
    def parse_lib(self):
        #ツイートライブラリを解析し、対象の原文とParseしたものをそれぞれ別ファイルに保存する
        with open(self.f_list['t_list'], encoding='utf-8') as t_list, \
                open(self.f_list['t_parsed'], mode='w', encoding='utf-8') as t_parsed, \
                    open(self.f_list['t_lib'], mode='a', encoding='utf-8') as t_lib:
            tweet = ''
            for line in t_list:
                if line == '\n': continue
                if line == '\{\n':
                    tweet = line
                elif line == '\}\n' and tweet != '\{\n':
                    tweet += line
                    tokens = re.split(' |\n',tweet)
                    flag = True
                    for token in tokens:
                        if token == 'RT' or (len(token) > 0 and token[0] == '@') or \
                            (len(token) > 3 and token[0:4] == 'http'):
                            flag = False
                            break
                    if flag:
                        t_parsed.write(self.cabocha.parse(tweet[3:-4]).toString(CaboCha.FORMAT_LATTICE))
                        t_lib.write(tweet)
                else:
                    tweet += line
    def line_chunks(self,fname_parsed):
        #引数:なし 返り値:一文に含まれる文節クラスのリスト
        with open(fname_parsed, encoding='utf-8') as f_parsed:
            chunks = dict()
            idx = -1
            pattern = []
            for line in f_parsed:
                if line == 'EOS\n':
                    if len(chunks) > 0:
                        sorted_tuple = sorted(chunks.items(), key=lambda x: x[0])
                        yield list(zip(*sorted_tuple))[1]
                        chunks.clear()
                    else:
                        yield []
                elif line[0] == '*':
                    #if pattern != []: print(pattern[0][0]+'\t'+pattern[-1][0])
                    pattern = []
                    cols = line.split(' ')
                    if len(cols) > 1:
                        idx = int(cols[1])
                        dst = int(re.search(r'(.*?)D', cols[2]).group(1))
                        if idx not in chunks:
                            chunks[idx] = Chunk()
                        chunks[idx].dst = dst
                        if dst != -1:
                            if dst not in chunks:
                                chunks[dst] = Chunk()
                            chunks[dst].srcs.append(idx)
                else:
                    cols = line.split('\t')
                    res_cols = cols[1].split(',')
                    chunks[idx].morphs.append(
                        Morph(
                            cols[0],        # surface
                            res_cols[6],    # base
                            res_cols[0],    # pos
                            res_cols[1]     # pos1
                        )
                    )
                    pattern.append([cols[0],res_cols[0]])
            raise StopIteration
    def get_nouns(self):
        #文節中に存在する名詞を取り出しファイルに書き込む
        for chunks in self.line_chunks(self.f_list['t_parsed']):
            for chunk in chunks:
                if chunk.morphs[0].pos == '名詞':
                    if len(chunk.morphs) == 1:
                        with open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+chunk.morphs[0].pos1+'_'+'.txt', mode='a', encoding='utf-8') as fname:
                            fname.write(chunk.normalized_surface()+'\n')
                    elif chunk.morphs[-1].pos == '助詞':
                        with open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+chunk.morphs[0].pos1+'_'+chunk.morphs[-1].surface+'_'+chunk.morphs[-1].pos+'_'+chunk.morphs[-1].pos1+'_'+'.txt', mode='a', encoding='utf-8') as fname:
                            fname.write(chunk.normalized_surface()+'\n')
                    elif chunk.morphs[-1].pos == '助動詞':
                        with open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+chunk.morphs[0].pos1+'_'+chunk.morphs[-1].surface+'_'+chunk.morphs[-1].pos+'_'+chunk.morphs[-1].pos1+'_'+'.txt', mode='a', encoding='utf-8') as fname:
                            fname.write(chunk.normalized_surface()+'\n')
                    elif chunk.morphs[-1].pos == '記号':
                        if chunk.morphs[-2].pos == '助詞':
                            with open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+chunk.morphs[0].pos1+'_'+chunk.morphs[-1].surface+'_'+chunk.morphs[-1].pos+'_'+chunk.morphs[-1].pos1+'_'+chunk.morphs[-2].surface+'_'+chunk.morphs[-2].pos+'_'+chunk.morphs[-2].pos1+'_'+'.txt', mode='a', encoding='utf-8') as fname:
                                fname.write(chunk.normalized_surface()+'\n')
                        else:
                            with open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+'_'+'_'+chunk.morphs[-1].pos+'_'+chunk.morphs[-1].pos1+'_'+'.txt', mode='a', encoding='utf-8') as fname:
                                fname.write(chunk.normalized_surface()+'\n')
                    else:
                        with open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+'_'+'_'+chunk.morphs[-1].pos+'_'+'_'+'.txt', mode='a', encoding='utf-8') as fname:
                            fname.write(chunk.normalized_surface()+'\n')
    def make_tweet(self):
        #任意の文章に対して名詞の置換を行い、ツイートする内容をファイルに書き込む
        self.parse_lib()
        self.get_nouns()
        words = open(self.f_list['t_lib'],"r", encoding='utf-8').readlines()
        b_list = -1
        while words[b_list] != '\{\n':
            b_list = random.randint(0,len(words)-1)
        e_list = b_list
        while words[e_list] != '\}\n':
            e_list += 1
        o_word = words[b_list+1:e_list]

        word = ''
        for line in o_word:
            with open(self.f_list['target_parsed'], mode='w', encoding='utf-8') as o_parsed_word:
                o_parsed_word.write(self.cabocha.parse(line).toString(CaboCha.FORMAT_LATTICE))
            for chunks in self.line_chunks(self.f_list['target_parsed']):
                for chunk in chunks:
                    if chunk.morphs[0].pos == '名詞':
                        if len(chunk.morphs) == 1:
                            word += "".join(random.sample(open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+chunk.morphs[0].pos1+'_'+'.txt',"r", encoding='utf-8').readlines(),1))[:-1]
                        elif chunk.morphs[-1].pos == '助詞':
                            word += "".join(random.sample(open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+chunk.morphs[0].pos1+'_'+chunk.morphs[-1].surface+'_'+chunk.morphs[-1].pos+'_'+chunk.morphs[-1].pos1+'_'+'.txt',"r", encoding='utf-8').readlines(),1))[:-1]
                        elif chunk.morphs[-1].pos == '助動詞':
                            word += "".join(random.sample(open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+chunk.morphs[0].pos1+'_'+chunk.morphs[-1].surface+'_'+chunk.morphs[-1].pos+'_'+chunk.morphs[-1].pos1+'_'+'.txt',"r", encoding='utf-8').readlines(),1))[:-1]
                        elif chunk.morphs[-1].pos == '記号':
                            if chunk.morphs[-2].pos == '助詞':
                                word += "".join(random.sample(open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+chunk.morphs[0].pos1+'_'+chunk.morphs[-1].surface+'_'+chunk.morphs[-1].pos+'_'+chunk.morphs[-1].pos1+'_'+chunk.morphs[-2].surface+'_'+chunk.morphs[-2].pos+'_'+chunk.morphs[-2].pos1+'_'+'.txt',"r", encoding='utf-8').readlines(),1))[:-1]
                            else:
                                word += "".join(random.sample(open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+'_'+'_'+chunk.morphs[-1].pos+'_'+chunk.morphs[-1].pos1+'_'+'.txt',"r", encoding='utf-8').readlines(),1))[:-1]
                        else:
                            word += "".join(random.sample(open(self.path['app_lib']+'/'+chunk.morphs[0].pos+'_'+'_'+'_'+chunk.morphs[-1].pos+'_'+'_'+'.txt',"r", encoding='utf-8').readlines(),1))[:-1]
                    else:
                        word += chunk.normalized_surface()
            word += '\n'
        with open(self.f_list['containts'], mode='w', encoding='utf-8') as out_file:
            out_file.write("".join(word[:-1]))

lang_pro = lang_pro()
lang_pro.make_tweet()
