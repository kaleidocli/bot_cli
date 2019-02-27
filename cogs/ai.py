import discord
from discord.ext import commands
from nltk.tokenize import word_tokenize
from time import sleep
import random


class ai:
    def __init__(self, client):
        self.client = client
        self.in_msg = ''
        self.out_msg = ''
        self.msg_type = ''
        self.Qfile_get()
        self.VoVfile_get()
        self.VoSfile_get()
        self.VoNfile_get()

    in_msg = ''
    out_msg = ''
    msg_type = ''

    Q_type = ''; Q_YN = []; Q_WHAT = []; Q_WHEN = []; Q_WHY = []; Q_WHICH = []; Q_WHO = []; Q_WHO_2 = []; Q_HOW = []; Q_HMUCH = []; Q_WHERE = []
    N_food = []
    S_1P = []; S_2P = []; S_3P = []; S_3P_plu = []; S_NounP = []
    intra_S = []; tra_S = []; S = []; M_1 = []; M_2 = []; M_3 = []

    async def on_message(self, message):
        if 'cli' in message.content or 'Cli' in message.content:
            author = message.author
            content = message.content
            channel = message.channel
            self.anal_msg(content.lower(), author)
            try:
                await self.client.send_message(channel, out_msg)
            except:
                pass
            sleep(0.5)

    def anal_msg(self, msg, auth):
        global out_msg
        global Q_type
        msg_list = word_tokenize(msg)
        if 'chào' in msg_list:
            out_msg = f"chào chào cmm {auth.name} -__-"
        else:
            out_msg = ''
        print("-------------------------------------")

        self.dist_msg(msg_list)
        #out_msg = Q_type

    def dist_msg(self, msgl):
        global msg_type
        if '?' in msgl:
            msg_type = 'Q'                                                           #Questions
            self.dist_Q(msgl)
        elif '!' in msgl:
            msg_type = 'E'                                                           #Exclamatory Sentences
        elif '?' in msgl and '!' in msgl:
            msg_type = 'EQ'                                                          #Both Questions and Exclamatory
        else:
            msg_type = 'A'                                                           #Affirmative Sentences

    def dist_Q(self, msgl):
        global Q_YN
        global Q_WHAT
        global Q_WHEN
        global Q_WHY 
        global Q_WHICH
        global Q_WHO
        global Q_WHO_2
        global Q_HOW
        global Q_HMUCH
        global Q_type

        global S
        print(msgl)
        if bool(set(Q_YN).intersection(msgl[int(msgl.index('?') - 2):msgl.index('?')])) == True:                            #2 từ sau dấu chấm hỏi phải trùng với những từ trong Q_YN list
            Q_type = 'YN'
            self.dist_Q_YN(msgl)
        elif bool(set(Q_WHAT).intersection(msgl[int(msgl.index('?') - 4):msgl.index('?')])) == True:
            Q_type = 'WHAT'
        elif bool(set(Q_WHO).intersection(msgl[:msgl.index('?')])) == True:
            Q_type = 'WHO'
        elif 'đâu' in msgl:
            if 'đâu' in msgl[int(msgl.index('?') - 2):msgl.index('?')]:
                Q_type = 'WHERE'
            elif 'ở' == msgl[int(msgl.index('đâu') - 1)] or 'chỗ' == 'ở' == msgl[int(msgl.index('đâu') - 1)]:
                Q_type = 'WHERE'
            elif bool(set(S).intersection(msgl[int(msgl.index('đâu') - 2) : msgl.index('đâu')])):
                Q_type = 'WHERE'
        elif msgl[len(msgl) - 1] in ['vậy', 'thế', 'được']:
            if 'sao' in msgl:
                if msgl[(msgl.index('thế') - 1)] in ['được', 'hay', 'ổn', 'tốt', 'tuyệt', 'ngon', 'đẹp', 'xinh', 'thơm']:
                    Q_type = 'HOW'
                else:
                    Q_type = 'WHY'
        elif bool(set(Q_WHY).intersection(msgl[:-1])) == True:
            Q_type = 'WHY'
        elif 'nào' in msgl[:msgl.index('?')]:
            if bool(set(Q_WHEN).intersection(msgl[:msgl.index('nào')])) == True:                                            #khi, chừng, hồi, lúc
                Q_type = 'WHEN'
            elif bool(set(Q_WHO_2).intersection(msgl[int(msgl.index('nào') - 2):msgl.index('nào')])) == True:
                Q_type = 'WHO'
            elif msgl[(msgl.index('nào') - 1)] in Q_HOW:                                                                    #cách, thế
                Q_type = 'HOW'
            elif 'chỗ' in msgl[int(msgl.index('nào') - 2):msgl.index('nào')]:
                Q_type = 'WHERE'
            else:
                Q_type = 'WHICH'
        elif bool(set(Q_HMUCH).intersection(msgl[:(msgl.index('?') - 1)])) == True:
            Q_type = 'H_MUCH'
        else:
            Q_type = 'Sorry akn-san didnt teach me well :<'

    def dist_Q_YN(self, msgl):
        global intra_S; global tra_S; global M_1; global M_2; global M_3
        YN_type = ''
        YNa_mtype = ''
        sub_type = ''
        v_type = ''; v_subtype = []
        n_key = ''
        obj = ''

        #Get object's elements from msgl, then get the obj rep.
        v_key, v_type, v_subtype, n_key = self.obj_get(msgl)
        obj = self.obj_rep(v_key, n_key)
        print(v_key)
        
        #Lấy YN_key (không, chưa) của Q_YN
        YN_key = ''.join(list(set(Q_YN).intersection(msgl[int(msgl.index('?') - 2):msgl.index('?')])))

        #Check if YN_type is active or passive.
        if not v_key:                                                                               #if list is empty
            YN_type = 'passive'
        else:
            YN_type = 'active'
        print(f"<{YN_type}>")

        if YN_type == 'active':
            #Check the meaning type of Q_YN
            YNa_mtype = self.dist_type_YNa(msgl, v_key[0], v_subtype)

            sub = self.sub_get(msgl, v_key)
            sub, sub_type = self.sub_dist(msgl, sub)
            print(YNa_mtype)
            self.rep(msgl, YNa_mtype, YN_key, sub, sub_type, obj)
        print(f"<{sub}>")

    def dist_type_YNa(self, msgl, verb, v_subtype):
        global Q_YN
        YN_key = ''
        YNa_mtype = ''

        YN_key = ''.join(list(set(Q_YN).intersection(msgl[int(msgl.index('?') - 2):msgl.index('?')])))
        if YN_key in ['không', 'ko', 'hem', 'hông', 'nha', 'ha']:
            if 'M_1ba' in v_subtype:
                if msgl[int(msgl.index(verb) - 1)] in ['nào', 'giờ'] and msgl[int(msgl.index(verb) - 2)] in ['khi', 'bao', 'lúc'] or msgl[int(msgl.index(verb) - 1)] == 'từng':
                    YNa_mtype = '5'
                elif msgl[int(msgl.index(YN_key) - 1)] in ['nào', 'giờ'] and msgl[int(msgl.index(YN_key) - 2)] in ['khi', 'bao', 'lúc']:
                    YNa_mtype = '5'
                elif msgl[int(msgl.index(YN_key) - 1)] in ['được', 'nổi']:
                    YNa_mtype = '3'
                else:
                    YNa_mtype = '2'
            else:
                if msgl[int(msgl.index(verb) - 1)] in ['nào', 'giờ'] and msgl[int(msgl.index(verb) - 2)] in ['khi', 'bao', 'lúc'] or msgl[int(msgl.index(verb) - 1)] == 'từng':
                    YNa_mtype = '5'
                elif msgl[int(msgl.index(YN_key) - 1)] in ['nào', 'giờ'] and msgl[int(msgl.index(YN_key) - 2)] in ['khi', 'bao', 'lúc']:
                    YNa_mtype = '5'
                elif msgl[int(msgl.index(YN_key) - 1)] in ['được', 'nổi']:
                    YNa_mtype = '3'
                else:
                    YNa_mtype = '1'
        elif YN_key in ['chưa']:
            if bool(set(['đã', 'có']).intersection(msgl[int(msgl.index(verb) - 3) : msgl.index(verb)])) == True:
                if msgl[int(msgl.index(verb) - 1)] in ['nào', 'giờ'] and msgl[int(msgl.index(verb) - 2)] in ['khi', 'bao', 'lúc'] or msgl[int(msgl.index(verb) - 1)] == 'từng':
                    YNa_mtype = '5'
                elif msgl[int(msgl.index(YN_key) - 1)] in ['được', 'nổi']:
                    YNa_mtype = '3'
                else:
                    YNa_mtype = '4'
            else:
                if msgl[int(msgl.index(verb) - 1)] in ['nào', 'giờ'] and msgl[int(msgl.index(verb) - 2)] in ['khi', 'bao', 'lúc'] or msgl[int(msgl.index(verb) - 1)] == 'từng':
                    YNa_mtype = '5'
                elif msgl[int(msgl.index(YN_key) - 1)] in ['được', 'nổi']:
                    YNa_mtype = '3'
                else:
                    YNa_mtype = '4'
        return YNa_mtype

    def verb_get(self, msgl):
        global intra_S; global tra_S; global M_1; global M_2; global M_3
        vocab_list = intra_S + tra_S + M_1 + M_2 + M_3
        v_key = []
        v_key_temp = []
        key_list = []
        gerund = []
        msgl_temp = msgl.copy()
        
        #if 'chưa' in msgl[:int(msgl.index('?'))]:
        #Scan through the verbs' lists for the verbs.
        for i in msgl[:int(msgl.index('?'))]:
            try:
                if i in vocab_list:
                    v_key_temp = [i]
                else:
                    v_key_temp.clear()
                if v_key_temp:
                    v_key = v_key + v_key_temp
            except:
                pass

        print(v_key)
        #Find GERUND by checking if a verb's a gerund in msgl_temp. If not, remove the verb out of msgl_temp. Otherwise, pop() the gerund out of msgl_temp.
        for i in v_key:
            try:
                if msgl_temp[int(msgl_temp.index(i) - 1)] in ['đồ', 'thức', 'cách']:
                    gerund.append(f"{msgl_temp[int(msgl.index(i) - 1)]} {v_key.pop(int(v_key.index(i)))}")
                else:
                    del msgl_temp[int(msgl_temp.index(i))]
            except IndexError:
                print("[Gerund] No prefix in front of verb > out of index.")
        print(f"ger: {gerund}")

        #Rearrange elements in v_key to match the order in msgl
        for i in v_key:
            key_list.append(msgl.index(i))
        v_key.clear()
        key_list.sort()
        for i in key_list:
            v_key.append(msgl[i])
        
        return v_key

    def verb_dist(self, msgl, v_key):
        global intra_S; global tra_S; global M_1; global M_2; global M_3; global S
        v_type = ''; type = ''; v_subtype = []; v_mkey = []

        #Due to performance reasons, we'll try to avoid scanning the whole S list.
        v_type = self.verb_dist_Engine(msgl, v_key[-1])
        if len(v_key) > 1:
            for i in v_key[:int(msgl.index(v_key[-1]))]:
                type = self.verb_dist_Engine(msgl, i)
                if type not in ['intra_S', 'tra_S']:
                    pass
                else:
                    v_mkey.append(i)
                v_subtype.append(self.verb_dist_Engine(msgl, i))
            v_mkey.append(v_key[:int(msgl.index(v_key[-1]))])
        else:
            v_mkey = v_key.copy()
        
        return v_type, v_subtype, v_mkey

    def verb_dist_Engine(self, msgl, v):
        global intra_S; global tra_S; global M_1; global M_2; global M_3; global S
        v_type = ''

        if v in intra_S:
            v_type = 'intra_S'
        elif v in tra_S:
            v_type = 'tra_S'
        elif v in M_1:
            if v in ['nên', 'phải', ' cần']:
                if v == 'cần':
                    v_type = 'M_1aa'
                else:
                    v_type = 'M_1a'
            elif v == 'thể':
                if msgl[int(msgl.index(v) - 1)] == 'có':
                    v_type = 'M_1ba'
                elif msgl[int(msgl.index(v) - 1)] == 'không':
                    v_type = 'M_1bb'
                elif msgl[int(msgl.index(v) - 1)] == 'chưa':
                    v_type = 'M_1bc'
            elif v in ['bị', 'được', 'mắc']:
                v_type = 'M_1c'
            elif v in ['mong', 'muốn', 'trông', 'ước', 'cầu']:
                v_type = 'M_1d'
            elif v in ['dám', 'định', 'nỡ', 'thôi', 'đành']:
                v_type = 'M_1e'
        elif v in M_2:
            if v == 'có':
                v_type = 'M_2a'
            elif v == 'hết':
                v_type = 'M_2b'
            elif v == 'còn':
                v_type = 'M_2c'
        elif v in M_3:
            v_type = 'M_3'
        else:
            print("[verb_dist_Engine()] Verb not found!")

        return v_type

    def sub_get(self, msgl, v_key):
        global S_1P
        global S_2P
        global S_3P
        global S_3P_plu
        global S_NounP
        sub_list = [S_1P, S_2P, S_3P, S_3P_plu, S_NounP]
        sub_key = []
        sub_key_temp = []
        key_list = []

        #Scan through msgl for subject(s)
        for i in sub_list:
            try:
                sub_key_temp = list(set(msgl[:msgl.index(v_key[0])]).intersection(set(i)))
                if sub_key_temp:
                    sub_key = sub_key + sub_key_temp
            except:
                pass

        #Rearrange elements in sub_key to match the msgl
        for i in sub_key:
            key_list.append(msgl.index(i))
        sub_key.clear()
        key_list.sort()
        for i in key_list:
            sub_key.append(msgl[i])
        
        try:
            return sub_key[int(len(sub_key) - 1)]
        except:
            print('Error: Trước verb ko có gì')

    def sub_dist(self, msgl, sub):
        global S_1P
        global S_2P
        global S_3P
        global S_3P_plu
        global S_NounP
        s_type = ''

        if sub in S_1P:
            if msgl[(int(msgl.index(sub)) - 1)] in ['bọn', 'tụi', 'đám', 'bọn']:
                sub = f"{msgl[(int(msgl.index(sub)) - 1)]} {sub}"
                s_type = '1P_plu'
            else:
                s_type = '1P'
        elif sub in S_2P:
            if msgl[(int(msgl.index(sub)) - 1)] in ['bọn', 'tụi', 'đám', 'chúng', 'mấy']:
                sub = f"{msgl[(int(msgl.index(sub)) - 1)]} {sub}"
                s_type = '2P_plu'
            elif msgl[(int(msgl.index(sub)) + 1)] in ['ấy', 'đó']:
                if msgl[(int(msgl.index(sub)) - 1)] in ['bọn', 'tụi', 'đám', 'chúng', 'mấy']:
                    sub = f"{msgl[(int(msgl.index(sub)) - 1)]} {sub}"
                    sub = f"{sub} {msgl[(int(msgl.index(sub)) + 1)]}"
                    s_type = '3P_plu'
                else:
                    sub = f"{sub} {msgl[(int(msgl.index(sub)) + 1)]}"
                    s_type = '3P'
            else:
                s_type = '2P'
        elif sub in S_NounP:
            if msgl[(int(msgl.index(sub)) - 1)] in ['bọn', 'tụi', 'đám', 'chúng', 'mấy']:
                sub = f"{msgl[(int(msgl.index(sub)) - 1)]} {sub}"
                s_type = '1P_plu'
            elif msgl[(int(msgl.index(sub)) + 1)] in ['ấy', 'đó']:
                if msgl[(int(msgl.index(sub)) - 1)] in ['bọn', 'tụi', 'đám', 'chúng', 'mấy']:
                    sub = f"{msgl[(int(msgl.index(sub)) - 1)]} {sub}"
                    sub = f"{sub} {msgl[(int(msgl.index(sub)) + 1)]}"
                    s_type = '3P_plu'
                else:
                    sub = f"{sub} {msgl[(int(msgl.index(sub)) + 1)]}"
                    s_type = '3P'
            else:
                s_type = '1P'
        elif sub in S_3P:
            if msgl[(int(msgl.index(sub)) - 1)] in ['bọn', 'tụi', 'đám', 'chúng', 'mấy']:
                sub = f"{msgl[(int(msgl.index(sub)) - 1)]} {sub}"
                s_type = '3P_plu'
            elif msgl[(int(msgl.index(sub)) + 1)] in ['ấy', 'đó']:
                sub = f"{sub} {msgl[(int(msgl.index(sub)) + 1)]}"
                s_type = '3P'
            else:
                s_type = '3P'
        elif sub in S_3P_plu:
            s_type = '3P_plu'
        return sub, s_type

    def sub_rep(self, sub, sub_type):
        global S_1P; global S_2P; global S_3P; global S_3P_plu; global S_NounP
        sub_A = ''

        if sub_type == '1P':
            sub_A = random.choice(S_2P)
        elif sub_type == '1P_plu':
            sub_A = f"{word_tokenize(sub)[0]} {random.choice(S_2P)}"
        elif sub_type == '2P':
            sub_A = random.choice(S_1P)
        elif sub_type == '2P_plu':
            sub_A = f"{word_tokenize(sub)[0]} {random.choice(S_1P)}"
        elif sub_type == '3P':
            if sub in ['thằng', 'tên', 'gã']:
                sub_A = f"{sub} {random.choice(['đấy', 'đó'])}"
            else:
                    sub_A = sub
        elif sub_type == '3P_plu':
            if sub in ['thằng', 'tên', 'gã']:
                sub_A = f"{sub} {random.choice(['đấy', 'đó'])}"
            else:
                sub_A = sub    
        return sub_A

    def obj_get(self, msgl):
        v_key = self.verb_get(msgl)
        v_type, v_subtype, v_mkey = self.verb_dist(msgl, v_key)
        n_key = []

        #Decide if get verb or not
        if v_type == 'intra_S':
            pass
        elif v_type == 'tra_S':
            n_key.append(self.noun_get(msgl, v_key))
        elif v_type == 'M_1aa':
            n_key.append(self.noun_get(msgl, v_key))
        elif v_type == 'M_1c':
            n_key.append(self.noun_get(msgl, v_key))             #star + adj
        elif v_type == 'M_1d':
            n_key.append(self.noun_get(msgl, v_key))
        elif v_type in ['M_2a', 'M_2b', 'M_2c']:
            n_key.append(self.noun_get(msgl, v_key))             #adj
        elif v_type == 'M_3':
            n_key.append(self.noun_get(msgl, v_key))

        return v_key, v_type, v_subtype, n_key    

    def obj_rep(self, v_key, n_key):
        obj = ''
        noun = ''
        verb = ' '.join(v_key)
        try:
            noun = ' '.join(n_key)
        except TypeError:
            pass

        obj = f"{verb + ' '}{noun}"

        return obj

    def noun_get(self, msgl, v_key):
        global N_food
        n_key = []
        n_key_temp = []
        key_list = []

        for i in N_food:
            try:
                if set([word_tokenize(i)]).issubset(set(msgl[int(msgl.index(v_key[-1]) + 1):])):
                    n_key_temp = [i]
                else:
                    n_key_temp.clear()
                if n_key_temp:
                    n_key = n_key + n_key_temp
            except:
                pass

        #Rearrange elements in n_key to match the msgl
        if n_key:
            for i in n_key:
                key_list.append(msgl.index(i))
            n_key.clear()
            key_list.sort()
            for i in key_list:
                n_key.append(msgl[i])
        
        print(f"<{n_key}>")
        try:
            return n_key[0]
        except:
            print('Error: Sau verb ko có noun.')

    def rep(self, msgl, YNa_mtype, YN_key, sub, sub_type, obj):
        global S_1P; global S_2P; global S_3P; global S_3P_plu; global S_NounP
        global out_msg
        A_type = ''
        #Cho ra subject sub_A tương phản với subject của câu hỏi.
        sub_A = str(self.sub_rep(sub, sub_type))

        A_type = random.choice(['y', 'n'])
        if A_type == 'y':
            if YNa_mtype == '1':
                out_msg = f"Okie"
            elif YNa_mtype == '2':
                out_msg = f"Có"
            elif YNa_mtype == '3':
                if YN_key in ['không', 'ko', 'hem', 'hông', 'nha', 'ha']:
                    if sub_type in ['2P', '2P_plu']:
                        sub_A = sub_A.capitalize()
                        out_msg = f"Được"
                    elif sub_type in ['1P', '1P_ple']:
                        out_msg = f"Được rồi đó"
                elif YN_key in ['chưa']:
                    if sub_type in ['2P', '2P_plu']:
                        sub_A = sub_A.capitalize()
                        out_msg = f"Được"
                    elif sub_type in ['1P', '1P_ple']:
                        out_msg = f"Rồi"
            elif YNa_mtype == '4':
                out_msg = f"Rồi"
            elif YNa_mtype == '5':
                out_msg = f"Rồi"
            else:
                print("ERROR: Unable to recognize YN_type in yes!")
        elif A_type == 'n':
            if YNa_mtype == '1':
                out_msg = f"Không"
            elif YNa_mtype == '2':
                out_msg = f"Không"
            elif YNa_mtype == '3':
                if YN_key in ['không', 'ko', 'hem', 'hông', 'nha', 'ha']:
                    if sub_type in ['2P', '2P_plu']:
                        out_msg = f"Không được"
                    elif sub_type in ['1P', '1P_ple']:
                        out_msg = f"Không"
                elif YN_key in ['chưa']:
                    if sub_type in ['2P', '2P_plu']:
                        out_msg = f"Chưa"
                    elif sub_type in ['1P', '1P_ple']:
                        out_msg = f"Méo"
            elif YNa_mtype == '4':
                out_msg = f"Chưa"
            elif YNa_mtype == '5':
                out_msg = f"Chưa"
            else:
                print("ERROR: Unable to recognize YN_type in no!")
            

    def Qfile_get(self):                                                                               #Tất cả các file keywords phải được save dưới UTF-8
        global Q_YN 
        global Q_WHAT 
        global Q_WHEN 
        global Q_WHY 
        global Q_WHICH 
        global Q_WHO 
        global Q_WHO_2
        global Q_HOW 
        global Q_HMUCH
        global Q_WHERE
        with open('Q_YN.txt', 'r', encoding='utf-8-sig') as f:                                             #Q_YN.txt chứa những key word của YN questions
            Q_YN = word_tokenize(f.read())
        with open('Q_WHAT.txt', 'r', encoding='utf-8-sig') as f:                                           #Q_WHAT.txt chứa những key word của WHAT questions
            Q_WHAT = word_tokenize(f.read())
        with open('Q_WHEN.txt', 'r', encoding='utf-8-sig') as f:                                           #Q_WHAT.txt chứa những key word của WHAT questions
            Q_WHEN = word_tokenize(f.read())
        with open('Q_WHY.txt', 'r', encoding='utf-8-sig') as f:                                           #Q_WHAT.txt chứa những key word của WHAT questions
            Q_WHY = word_tokenize(f.read())
        with open('Q_WHICH.txt', 'r', encoding='utf-8-sig') as f:                                           #Q_WHAT.txt chứa những key word của WHAT questions
            Q_WHICH = word_tokenize(f.read())
        with open('Q_WHO.txt', 'r', encoding='utf-8-sig') as f:                                           #Q_WHAT.txt chứa những key word của WHAT questions
            Q_WHO = word_tokenize(f.read())
        with open('Q_WHO_2.txt', 'r', encoding='utf-8-sig') as f:
            Q_WHO_2 = word_tokenize(f.read())
        with open('Q_HOW.txt', 'r', encoding='utf-8-sig') as f:                                           #Q_WHAT.txt chứa những key word của WHAT questions
            Q_HOW = word_tokenize(f.read())
        with open('Q_HMUCH.txt', 'r', encoding='utf-8-sig') as f:
            Q_HMUCH = word_tokenize(f.read())
        with open('Q_WHERE.txt', 'r', encoding='utf-8-sig') as f:
            Q_WHERE = word_tokenize(f.read())

    def VoVfile_get(self):
        global S
        global intra_S
        global tra_S
        global M_1
        global M_2
        global M_3

        with open("vocab/verb/intra_S.txt", 'r', encoding='utf-8-sig') as f:
            intra_S = word_tokenize(f.read())
        with open("vocab/verb/tra_S.txt", 'r', encoding='utf-8-sig') as f:
            tra_S = word_tokenize(f.read())
        with open("vocab/verb/M_1.txt", 'r', encoding='utf-8-sig') as f:
            M_1 = word_tokenize(f.read())
        with open("vocab/verb/M_2.txt", 'r', encoding='utf-8-sig') as f:
            M_2 = word_tokenize(f.read())
        with open("vocab/verb/M_3.txt", 'r', encoding='utf-8-sig') as f:
            M_3 = word_tokenize(f.read())
        S = intra_S + tra_S

    def VoSfile_get(self):
        global S_1P
        global S_2P
        global S_3P
        global S_3P_plu
        global S_NounP

        with open("vocab/subject/1P.txt", 'r', encoding='utf-8-sig') as f:
            S_1P = word_tokenize(f.read())
        with open("vocab/subject/2P.txt", 'r', encoding='utf-8-sig') as f:
            S_2P = word_tokenize(f.read())
        with open("vocab/subject/3P.txt", 'r', encoding='utf-8-sig') as f:
            S_3P = word_tokenize(f.read())
        with open("vocab/subject/3P_plu.txt", 'r', encoding='utf-8-sig') as f:
            S_3P_plu = word_tokenize(f.read())
        with open("vocab/subject/NounP.txt", 'r', encoding='utf-8-sig') as f:
            S_NounP = word_tokenize(f.read())

    def VoNfile_get(self):
        global N_food

        with open("vocab/noun/food/things.txt", 'r', encoding='utf-8-sig') as f:
            N_food = word_tokenize(f.read())

def setup(client):
    client.add_cog(ai(client))





