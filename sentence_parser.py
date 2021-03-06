import nltk
from nltk.corpus import wordnet as wn
from nltk import word_tokenize
import re

re_digits_v      = [r'\d+']
re_hour_corpus_v = [r'\bhs?\b', r'\bhours?\b']
re_mins_corpus_v = [r'\bm\b', r'\bminutes?\b', r'\bmins?\b']
re_add_corpus_v  = [r'\band\b', r'\bplus\b']

re_yes_corpus_v = [r'\by\b', r'\byes\b', r'\bok\b', r'\bokey\b', r"\bdid\b", r'\bwant\b', r'\bdo\b', r'affirmative', r'positive', r'exact', r'correct']
re_not_corpus_v = [r'\bn\b', r'\bnot?\b', r"\bdidt\b", r"\bdidn'?t\b", r"\bdon'?t\b", r'negative', 'nope']


numbers_1_9_d = {'one'         : 1,
                 'two'         : 2,
                 'three'       : 3,
                 'four'        : 4,
                 'five'        : 5,
                 'six'         : 6,
                 'seven'       : 7,
                 'eight'       : 8,
                 'nine'        : 9}

numbers_10_19_d = {'ten'         :10,
                   'eleven'      :11,
                   'twelve'      :12,
                   'thirteen'    :13,
                   'fourteen'    :14,
                   'fifteen'     :15,
                   'sixteen'     :16,
                   'seventeen'   :17,
                   'eighteen'    :18,
                   'nineteen'    :19}
             
numbers_20_90_d = {'twenty'      :20,
                   'thirty'      :30,
                   'forty'       :40,
                   'fifty'       :50,
                   'sixty'       :60,
                   'seventy'     :70,
                   'eighty'      :80,
                   'ninety'      :90}



action_select_keys_d = {'personal_info':  ['personal', 'edit', 'modify', 'profile'],
                        'help':           ['help'],
                        'record':         ['record', 'add', 'new'],
                        'stats':          ['stats', 'summary', 'statistics', 'results', 'status'],
                        'delete':         ['delete', 'erase', 'remove', 'reset', 'clear', 'clean'],
                        'cancel':         ['cancel', 'stop', 'quit', 'exit', 'back', 'return', 'select']}


class Sentence_parser:
    """ This class has the task of parsing sentences and retrieve relevant information """

    def __init__(self):
        return None


    def find_v(self, sentence, to_find_v):
        sentence = sentence.lower()
        found = False

        for w in to_find_v:
            if w in sentence:
                found = True
                break

        return found
        
    def yes_no_question(self, sentence):
        sentence = sentence.lower()

        
        f_yes = re.findall('|'.join(re_yes_corpus_v), sentence)            
        f_not = re.findall('|'.join(re_not_corpus_v), sentence)

        to_ret = None
        if len(f_yes) > 0:
            to_ret = True
        if len(f_not) > 0:
            to_ret =  False

        return to_ret

    def postag(self, sentence):
        """ Make a postag of a sentense """

        # Ensure that the sentense is in lower case
##        sentence = sentence.lower()
        
        # First tokenize
        tokens = nltk.word_tokenize(sentence)

        # postag
        postag_v = nltk.pos_tag(tokens)
        
        return postag_v

    def find_exercise(self, sentence, dist_th=0.2):
        sport_v = []

        ss_sport    = wn.synsets('sport')[0]
        ss_exercise = wn.synsets('exercise')[0]
        ss_practice = wn.synsets('practice')[0]
        
        pt_v = self.postag(sentence)
        if len(pt_v) > 1:
            for w, t in pt_v:
                if 'sport' in w or 'exe' in w or 'practi' in w:
                    continue
                    
                if ('NN' in t) or ('VB' in t):
                    ss_NN = wn.synsets(w)
                    d_sport    = [wn.path_similarity(ss, ss_sport,    simulate_root=False) for ss in ss_NN]
                    d_exercise = [wn.path_similarity(ss, ss_exercise, simulate_root=False) for ss in ss_NN]
                    d_practice = [wn.path_similarity(ss, ss_practice, simulate_root=False) for ss in ss_NN]
##                    print(d_sport)
##                    print(d_exercise)
                    d_v = [d for d in (d_sport + d_exercise + d_practice) if d is not None]
                    if len(d_v) > 0:
                        d_NN = max(d_v)
                    else:
                        d_NN = 0
                        
                    if d_NN > dist_th:
                        sport_v.append( [d_NN, w] )

        elif len(pt_v) == 1:
            sport_v.append( (1.0, pt_v[0][0]))

        if len(sport_v) == 0:
            return None
        else:
            sport_v.sort()
            return sport_v[0][1]
            
                    
        
    
    def find_name(self, sentence):
        """ Finds and returns a personal name in the sentence.
            If is not found, it return None"""
        name_v = []
        
        s_lower = sentence.lower()
        tokens_lower = nltk.word_tokenize(s_lower)
        
        present = None
        if 'is' in tokens_lower:
            present = 'is'
            
        if 'me' in tokens_lower:
            present = 'me'

        if 'am' in tokens_lower:
            present = 'am'
            
            
        pt_v = self.postag(sentence)
        jump = True
        if present is not None:
            for w, p in pt_v:
                if jump and w.lower() != present:
                    continue
                elif jump:
                    jump = False
                    continue

                if len(name_v) == 0 or 'NN' in p:
                    name_v.append( w )
                else:
                    break

        
        if len(name_v) == 0:
            if len(pt_v) == 1:
                name = pt_v[0][0]

                name_v.append(name)
                
            # First lets find "NNP"s
            for w, p in pt_v:
                if p == 'NNP':
                    name_v.append(w)
        
            if len(name_v) == 0:
                for w, p in pt_v:
                    if p == 'VBN':
                        name_v.append(w)


        if len(name_v) == 0:
            return None
        else:
            for i in range(len(name_v)):
                name_v[i] = name_v[i][0].upper() + name_v[i][1:].lower()
                
        return ' '.join(name_v)


    def parse_nums(self, sentence):
        # to lower
        sentence = sentence.lower()

        # Ensure spaces over digits and units
        sentence = re.sub(r'(\d)([a-z])', r'\1 \2', sentence)

        # Transform the conectors
        sentence = re.sub('|'.join(re_hour_corpus_v), r'H', sentence)
        sentence = re.sub('|'.join(re_mins_corpus_v), r'M', sentence)
        sentence = re.sub('|'.join(re_add_corpus_v),  r'A', sentence)

        sentence = re.sub('half', ' 30 M ', sentence)
        sentence = re.sub('quarter', ' 15 M ', sentence)
               
        # Reemplace of all the special caracters:
        for k, v in numbers_10_19_d.items():
            sentence = re.sub(k, str(v), sentence)

        # Reemplace compound numbers
        for k_dec, v_dec in numbers_20_90_d.items():
            for k_un, v_un in numbers_1_9_d.items():
                sentence = re.sub('{}.?{}'.format(k_dec, k_un), '{}'.format(v_dec+v_un), sentence)

        # Reemplace single numbers
        for k_un, v_un in numbers_1_9_d.items():
            sentence = re.sub('{}'.format(k_un), '{}'.format(v_un), sentence)

        # Filter relevant information
        parsed_v = re.findall(r'[A-Z]|\b\d+\b', sentence)

        # Numbers to int type
        parsed_v = [int(i) if i.isdigit() else i for i in parsed_v]

        return parsed_v


    def find_mins(self, sentence):
        parsed_v = self.parse_nums(sentence)
        
        # Calculate total minutes
        total_mins = 0
        for i in range(len(parsed_v)):
            if parsed_v[i] in ['A', 'M', 'H']:
                continue

            if type(parsed_v[i]) is int:
                if i+1 < len(parsed_v) and parsed_v[i+1] == 'H':
                    total_mins += 60 * parsed_v[i]
                else:
                    total_mins += parsed_v[i]
                    
        return total_mins



    def find_difficulty(self, sentence):
        parsed_v = self.parse_nums(sentence)

        difficulty = 5

        for i in parsed_v:
            if type(i) is int:
                difficulty = i
                break
            
        return difficulty
    


    def intension_detector(self, sentence, just_cancel=False, sim_th=0.6):
        """ returns the intention of the sentence.
            if just_cancel is present, justo compares the sentence with the cancel intention.
        """
        
        pos_actions_v = []

        if (not just_cancel) and self.find_v(sentence, action_select_keys_d['personal_info']):
            pos_actions_v.append('personal_info')
        elif (not just_cancel) and self.find_v(sentence, action_select_keys_d['help']):
            pos_actions_v.append('help')
        elif (not just_cancel) and self.find_v(sentence, action_select_keys_d['record']):
            pos_actions_v.append('record')
        elif (not just_cancel) and self.find_v(sentence, action_select_keys_d['stats']):
            pos_actions_v.append('stats')
        elif (not just_cancel) and self.find_v(sentence, action_select_keys_d['delete']):
            pos_actions_v.append('delete')
        elif self.find_v(sentence, action_select_keys_d['cancel']):
            pos_actions_v.append('cancel')
        

        if (not just_cancel) and (len(pos_actions_v) > 1 or len(pos_actions_v) == 0):
            # if we are here, we need desambigurate

            if len(pos_actions_v) == 0:
                pos_actions_v = list(action_select_keys_d.keys())
                
            actions_similarity_v = [0.0 for a in pos_actions_v]
            actions_synsets_v = []
            for a in pos_actions_v:
                actions_synsets_v.append([])
                for a_w in action_select_keys_d[a]:
                    ss_v = wn.synsets(a_w)
                    if len(ss_v) > 0:
                        actions_synsets_v[-1] += ss_v
                    
##            print(pos_actions_v)
##            for x in actions_synsets_v:
##                print()
##                print(x)
##            input()
                    
            tokens_v = nltk.word_tokenize(sentence)
            for i_a, action in enumerate(pos_actions_v): # for each action
                for w in tokens_v: # for each word in the sentence
                    w_ss_v = wn.synsets(w)
                    
                    for a_ss in actions_synsets_v[i_a]: # for each ss in the action
                        for w_ss in w_ss_v: # for each ss in the word

##                        if len(w_ss_v) > 0:
##                            w_ss = w_ss_v[0]
                            
                            d_sim = wn.path_similarity(w_ss, a_ss, simulate_root=False)
                            if d_sim is not None and d_sim > actions_similarity_v[i_a]:
                                actions_similarity_v[i_a] = d_sim
##                                print(w_ss, a_ss, d_sim)

##            print(actions_similarity_v)


            sim_max = max(actions_similarity_v)
            if sim_max > sim_th:
                i_max = actions_similarity_v.index( sim_max )
                pos_actions_v = [ pos_actions_v[i_max] ]
            else:
                pos_actions_v = []
                    
                

        # At this point we must have 1 option or None
        assert len(pos_actions_v) <= 1, " - ERROR, intension_detector, mode than 1 posible option"
        
        if len(pos_actions_v) == 0:
            return None
        else:
            return pos_actions_v[0]
        
        
    
if __name__ == '__main__':
    sp = Sentence_parser()
##    sp.find_mins('I run two hours around the square and a warm-up of 16 mins in my house.')


    sp = Sentence_parser()
    q_v = ['I want to add a new record',
           'I just want to view my results',
           'I want to clean my data',
           'back',
           'delete',
           'my name is sergio',
           'give me the status']

    for q in q_v:
        a = sp.intension_detector(q, False)
        print(q)
        print(a)
        print('')

##    ss_sport    = wn.synsets('sport')[0]
##    ss_exercise = wn.synsets('exercise')[0]
##
##    
##    ss_try   = wn.synsets('minute')[0]
##
##    sentence_v = ["please take account of boxing.",
##                  "my sport is football.",
##                  "my exercise is swimming.",
##                  "my sport is running",
##                  "I am practicing basketball right now"]
##
##    for s in sentence_v:
##        sport = sp.find_exercise(s)
##        print(sport)
    

            
##    tokens = nltk.word_tokenize(sentence)
##    tagged = nltk.pos_tag(tokens)
##
##    print(tagged)


##    sentence_v = ['I run over twenty two minutes and five al the gym and 9 hs round the park',
##                  'about twelve minutes around my house and 5h in the park and 8 hs 8 hour fifty five mins 9 min',
##                  '55']
##
##    sentence = sentence_v[1]
##    
##
##    for s in sentence_v:
##        print(s)
##        print(sp.find_mins(s))
##        print()


    
##    sentence = re.sub(r'(\d)([a-z])', r'\1 \2', sentence)


    
##    f_v = re.findall('|'.join(re_digits_v + re_hour_corpus_v + re_mins_corpus_v), sentence)
##    print(f_v)

##    sentence_r = re.sub('|'.join(re_hour_corpus_v), 'H', sentence)
##    print(sentence_r)
    

##    re.findall('\dhour', 'mdlskjd hour daldjkal')



##    sentense_v = ["hello, my name is sergio.",
##                  "Hello, my name is sergio.",
##                  "Call me Sergio Manuel",
##                  "Sergio",
##                  "Sergio Manuel",
##                  "my name is Adam",
##                  "my name is adam",
##                  "my name is Adam sandler."]
##    
##
##
##    
##
##    for s in sentense_v:
##        name = sp.find_name(s)
##        print(name)











