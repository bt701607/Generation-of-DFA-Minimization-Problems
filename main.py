from DFA          import DFA
from DFABuilder   import DFABuilder
from DFAExtender  import DFAExtender
from pdf_from_dfa import pdf_from_dfa

from copy import deepcopy


USE_DFA_BUILDER = True


# construct dfa

test_dfa = None

if USE_DFA_BUILDER:

    test_dfa = DFABuilder().mix(0,1,1,3).dfa()

else:

    test_dfa = DFA(
        ['a','b','c','d','e'],
        [1,2,3,4,5],
        [
            ((1,1),'a'),
            ((1,2),'b'),
            ((2,4),'c'),
            ((5,1),'d'),
            ((2,5),'e')
        ],
        1,
        [4,5]
    )

    test_dfa = DFA(
        ['0', '1'],
        ['AD', 'B', 'CE', 'G'],
        [
            (('AD','CE'),'1'),
            (('AD','G' ),'0'),
            
            (('B' ,'CE'),'0'),
            (('B' ,'CE'),'1'),
            
            (('CE','B' ),'0'),
            (('CE','AD'),'1'),
            
            (('G' ,'B' ),'0'),
            (('G' ,'CE'),'1'),
        ],
        'AD',
        ['CE']
    )


# extend dfa

orig_dfa = deepcopy(test_dfa)

test_dfa = DFAExtender(dfa = test_dfa).duplicate(1).dfa()


# generate graphical representation of original and extended dfa

pdf_from_dfa(orig_dfa, "1")
pdf_from_dfa(test_dfa, "2")