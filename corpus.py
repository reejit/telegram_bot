
notImplemented = "ErrDialog not implemented."

# Corpus file
corpus_d = {'on_start':[
["""Welcome to MrExerciseBot.
MrExerciseBot is here to help you record your daily exercise routine.
MrExerciseBot can understand natural language, even voice messages"""],
["Hello user!!!! I must advise you, to start recording your training exercises you must provide some information about you first."]],

'personal_info':[
    ["Please tell me your name:"],
    ["Very good {name}, Now tell me about the default sport you want to take account for?"],
    ["Okay I will save {default_sport} as your default sport. Is it correct?"],
    ["That is it {name}. Now we can start to take acount all your activities."]],
'personal_info_err':[
    [notImplemented],
    ["I was unable to understand your name. Please try again."],
    ["I was unable to understand your exercise. Please try again."],
    ["I am very sorry, please say me again your default sport again."],
    ["It was an Yes/No answer, I couldn't figure out your reply. Please try it again."]],
            
'actions':[
    ["Please tell me, what do you want to do? You can ask me for help if you need ..."],
    ["{name}, I can't understand the action you want to do, please try it again."]],
            
'help':[
    ["""There are a lot of thing that I can do for you:
- I can show you your last statistics
- I can edit your personal information
- I can add a new record of your training of today
- I can delete all your data (private and all records)"""] ],

'record':[
    ['Okey {name}, lets record your training of today.', 'did you practice {default_sport}?'],
    ['Please tell me what sport did you do today?'],
    ['How long did you do the exercise?'],
    ['How hard was the exercise? Please give me an indicator from 0 to 10'],
    ['Happy training {name}!!! Your data was saved.']],
'record_err':[
    [notImplemented],
    ["I was unable to understand your yes/no answer. Please try again."],
    ["I was unable to understand your exercise. Please try again."]],

'stats':[
    ["Okay, {name} let's see what you did ..."],
    ['- sport: {activity}, last {n_records} records.\n- your total time: {total_time}\n- record mean time: {mean_time}\n- your mean model was {mean_act_mode}'],
    ['Sorry {name}, you have records yet, Please make a record of your training before ask me the stats.']],


'cancel':[
    ['Okay, canceling las operation ...']],
'cancel_err':[
    ["Sorry, you can not Cancel this operaton.", "I can't help you if you don't give me some default information."]],

'delete':[
    ['I am prepared to delete all your data. All your private and records data will be lost.', "Still do you want to proceed?"],
    ['Ass you wish. Bye Bye {name} !!!'],
    ['Uff!!!, Okay {name} your data will remain safe.']],
'delete_err':[
    [notImplemented],
    ["I was unable to understand your yes/no answer. Please try again."]],

'end':[
    ['You have chosen stop interacting with MrExerciese. If you want to start to interacto again please send a "/start" command.']]}



action_select_keys_d = {'personal_info':  ['personal', 'info', 'edit', 'modi'],
                        'help':           ['help', 'what'],
                        'record':         ['rec', 'add', 'post'],
                        'stats':          ['give', 'stat'],
                        'delete':         ['delete', 'del'],
                        'cancel':         ['cancel', 'stop', 'quit', 'exit']}









