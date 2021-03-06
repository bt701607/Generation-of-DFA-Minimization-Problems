#!/usr/bin/env python

"""Command-line tool to generate DFA minimization problems."""

import pathlib
import argparse

from planarity import PygraphIndexErrorBug

import log

from dfa    import DFA
from build  import rand_min_dfa, next_min_dfa
from extend import DFANotExtendable, extend_dfa
from output import save_exercise


__all__ = []


_DEFAULT_OUTPUT = pathlib.Path('./output')

_BOOL_CHOICES = ('yes', 'no')

_ARGUMENTS = {
  'solution DFA' : (
  ('-k',    int, 2,      'alphabet size of generated DFAs'),
  ('-n',    int, 4,      'number of states of solution DFA'),
  ('-f',    int, 1,      'number of final states of solution DFA'),
  ('-dmin', int, 2,      'lower bound for D-value'),
  ('-dmax', int, 3,      'upper bound for D-value'),
  ('-ps',   str, 'yes',  'toggle whether solution DFA shall be planar', _BOOL_CHOICES),
  ('-b',    str, 'enum', 'toggle whether solution DFA shall be build by enumeration or randomization', ('enum','random'))),

  'task DFA' : (
  ('-e',    int, 2,      'number of distinct equivalent reachable state pairs in task DFA'),
  ('-u',    int, 1,      'number of unreachable states in task DFA'),
  ('-c',    str, 'yes',  'toggle whether all unreachable states shall be complete', _BOOL_CHOICES),
  ('-pt',   str, 'yes',  'toggle whether task DFA shall be planar', _BOOL_CHOICES)),

  'output' : (
  ('-out',  str, _DEFAULT_OUTPUT, 'working directory; here results will be saved'),
  ('-dfa',  str, 'no',   'toggle whether DFAs shall be printed to .dfa-files', _BOOL_CHOICES),
  ('-tex',  str, 'yes',  'toggle whether LaTeX-code shall be created from DFAs', _BOOL_CHOICES),
  ('-pdf',  str, 'yes',  'toggle whether PDFs shall be created from DFAs', _BOOL_CHOICES),
  ('-shuf', str, 'yes',  'toggle whether DFA labels shall be shuffled', _BOOL_CHOICES))
}

_EPILOG = '''
General Informations:
- for k <= 1 it is not guaranteed that creating e equivalent reachable state pairs works
- enumerated/randomized generation share their history of generated languages
- even if ps = pt = 1, it is not guaranteed that the DFA is drawn planar
- if the program is used and then used with a different -out parameter,
  the previously found DFAs and enumeration states are not transferred
'''


def main():
    """Main procedure of DFA minimization problem generator.
    
    Parses command-line arguments and builds solution and task DFA accordingly.
    Saves result and cleans up.
    """
    
    # add and check parameters

    class MyFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.MetavarTypeHelpFormatter, argparse.RawTextHelpFormatter):
        pass

    parser = argparse.ArgumentParser(
        description='Command-line tool to generate DFA minimization problems.',
        formatter_class=MyFormatter, epilog=_EPILOG)

    for groupName in _ARGUMENTS:
        group = parser.add_argument_group(groupName)
        
        for option in _ARGUMENTS[groupName]:
            if len(option) == 4:
                group.add_argument(option[0], type=option[1], default=option[2], 
                                   help=option[3])
            else:
                group.add_argument(option[0], type=option[1], default=option[2], 
                                   help=option[3], choices=option[4])
    
    
    args = parser.parse_args()
    
    strToBool = lambda x: x == 'yes'
    
    args.ps   = strToBool(args.ps)
    args.c    = strToBool(args.c)
    args.pt   = strToBool(args.pt)
    args.dfa  = strToBool(args.dfa)
    args.tex  = strToBool(args.tex)
    args.pdf  = strToBool(args.pdf)
    args.shuf = strToBool(args.shuf)
    
    args.out = pathlib.Path(args.out)
    
        
    if args.k > args.n:
        log.k_too_big()
        return
    
    if args.n < args.f:
        log.f_too_big()
        return
        
    if args.pt and not args.ps:
        log.invalid_p_options()
        return
    
    if args.k == 0 and args.e > 0:
        log.not_extendable()
        return
        
    if any(map(lambda x: x<0, (args.k, args.n, args.f, args.dmin, args.dmax, args.e, args.u))):
        log.neg_value()
        return
    
    if not args.out.exists() or not args.out.is_dir():
        log.creating_output_dir()
        args.out.mkdir()
        log.done()
        
    log.start(args)
    

    # construct solution dfa

    log.building_solution(args)
    
    build = next_min_dfa if args.b == 'enum' else rand_min_dfa

    solDFA = build(args.k, args.n, args.f, args.dmin, args.dmax, args.ps, args.out)

    if solDFA is None and args.b == 'enum':
        
        log.done()
        log.enum_finished()
        return
    
    log.done()


    # extend dfa
    
    log.extending_solution(args)
    
    for i in range(10):
    
        try:
        
            reachDFA, taskDFA = extend_dfa(solDFA, args.e, args.u, args.pt, args.c)
            
        except DFANotExtendable:
        
            log.failed()
            log.dfa_not_extendable(args)
            return
            
        except PygraphIndexErrorBug:
        
            log.failed()
            log.pygraph_bug('extending')
            
            if i == 9:
                log.pygraph_bug_abort(args)
                return
                
        else:
        
            log.done()
            break


    # generate graphical representation of solution and task dfa

    if args.dfa or args.tex or args.pdf:
        log.saving()
        save_exercise(solDFA, reachDFA, taskDFA, args.out, 
                      args.dfa, args.tex, args.pdf, args.shuf)
        log.done()
    else:
        log.no_saving()
    

    # clean up working directory
    
    log.cleaning()
    
    for f in args.out.iterdir():
        if f.suffix in ('.toc', '.aux', '.log', '.gz', '.bbl', '.blg', '.out'):
            f.unlink()
    
    log.done()
    


if __name__ == '__main__':

    main()
