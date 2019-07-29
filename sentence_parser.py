import nltk
from nltk.corpus import wordnet as wn
from nltk import word_tokenize
import re

re_digits_v      = [r'\d+']
re_hour_corpus_v = [r'\bhs?\b', r'\bhours?\b']
re_mins_corpus_v = [r'\bm\b', r'\bminutes?\b', r'\bmins?\b']

re_yes_corpus_v = [r'\by\b', r'\byes\b', r'\bok\b', r'\bokey\b', r"\bdid\b"]
re_not_corpus_v = [r'\bn\b', r'\bnot?\b', r"\bdidt\b", r"\bdidn?'t\b"]




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
                    d_v = [d for d in (d_sport + d_exercise) if d is not None]
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
        

        
    
sentence = 'about 244 hours and 5h for 8 hs 8 hour 5 mins 9 min'





if __name__ == '__main__':
    sp = Sentence_parser()

    
    ss_sport    = wn.synsets('sport')[0]
    ss_exercise = wn.synsets('exercise')[0]

    
    ss_try   = wn.synsets('minute')[0]

    sentence_v = ["please take account of boxing.",
                  "my sport is football.",
                  "my exercise is swimming.",
                  "my sport is running",
                  "I am practicing basketball right now"]

    for s in sentence_v:
        sport = sp.find_exercise(s)
        print(sport)
    

            
##    tokens = nltk.word_tokenize(sentence)
##    tagged = nltk.pos_tag(tokens)
##
##    print(tagged)
##    sentence = re.sub(r'(\d)([a-z])', r'\1 \2', sentence)
##    
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











