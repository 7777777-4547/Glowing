import re






class MuScript():
    
    patterns_not = [
        ( r'!\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)', r'not (\1)' ),
        ( r'!\s*([a-zA-Z_][a-zA-Z0-9_]*)',          r'not \1'   ),
        ( r'!\s*([a-zA-Z_][a-zA-Z0-9_.]*)',         r'not \1'   ),
    ]
    
    patterns_and = [
        ( r'(\w+)\s*&\s*(\w+)', r'\1 and \2' ),
        ( r'(\S+)\s*&\s*(\S+)', r'\1 and \2' ),
        ( r'\)\s*&\s*\(',         ') and ('  ),
    ]
    
    patterns_or = [
        ( r'(\w+)\s*\|\s*(\w+)', r'\1 or \2' ),
        ( r'(\S+)\s*\|\s*(\S+)', r'\1 or \2' ),
        ( r'\)\s*\|\s*\(',         ') or ('  ),
    ]
    
    patterns_ternary = [
        ( r'(\S+)\s*\?\s*(\S+)\s*:\s*(\S+)',           r'\2 if \1 else \3' ),
        ( r'([^?]+)\s*\?\s*("[^"]*")\s*:\s*("[^"]*")', r'\2 if \1 else \3' ),
    ]
    
    patterns_concat = [
        ( r'"([^"]*)"(\s*)\|\|(\s*)"([^"]*)"', r'"\1" + "\4"' ),
        ( r'(\w+)(\s*)\|\|(\s*)"([^"]*)"',     r'\1 + "\4"'   ),
        ( r'"([^"]*)"(\s*)\|\|(\s*)(\w+)',     r'"\1" + \4'   ),
        ( r'(\w+)(\s*)\|\|(\s*)(\w+)',         r'\1 + \4'     ),
    ]
    
    patterns_arithmetic = [
        ( r'(\d+)\s*\+\s*(\d+)',             r'\1 + \2'  ),  
        ( r'(\d+)\s*-\s*(\d+)',              r'\1 - \2'  ),   
        ( r'(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)', r'\1 * \2'  ),  
        ( r'(\d+)\s*/\s*(\d+)',              r'\1 / \2'  ),   
        ( r'(\d+)\s*%\s*(\d+)',              r'\1 % \2'  ),   
        ( r'(\d+)\s*\^\s*(\d+)',             r'\1 ** \2' ), 
    ]

    patterns_comparison = [
        ( r'(\d+)\s*>\s*(\d+)',  r'\1 > \2'  ),   
        ( r'(\d+)\s*<\s*(\d+)',  r'\1 < \2'  ),   
        ( r'(\d+)\s*>=\s*(\d+)', r'\1 >= \2' ), 
        ( r'(\d+)\s*!=\s*(\d+)', r'\1 != \2' ), 
        ( r'(\d+)\s*==\s*(\d+)', r'\1 == \2' ), 
    ]
        
    patterns_parentheses = [
         (r'\(([^()]*)\)', r'(\1)' ),
    ]
     
    patterns = patterns_not + patterns_and + patterns_or + patterns_ternary + patterns_concat + patterns_arithmetic + patterns_comparison + patterns_parentheses    
    
    def _check_and_convert(self, script_str: str):
        
        script_str_pylike = script_str
        
        for pattern, replacement in self.patterns:
            script_str_pylike = re.sub(pattern, replacement, script_str)
        
        return script_str_pylike
    
    
    def __init__(self, script_str: str):
        self.script_str = self._check_and_convert(script_str)
        
    
    def run(self):
        return eval(self.script_str)
        




