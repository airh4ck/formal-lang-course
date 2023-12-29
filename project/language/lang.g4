grammar lang;

WHITESPACE: [ \t\r] -> skip;
CHAR: [a-z] | [A-Z] | '_';
DIGIT: [0-9];
NONZERO: [1-9];
ID: CHAR (CHAR | DIGIT)*;

var: CHAR | ID;

STRING: '"' (CHAR | DIGIT | '_')* '"';
INT: NONZERO DIGIT*;
BOOL: 'true' | 'false';
REGEX: '/' ~[\n]* '/';
CFG: 'g' '/' ~[\n]* '/';

string: STRING;
int: DIGIT | INT;
bool: BOOL;
regex: REGEX;
cfg: CFG;

val: string | int | bool | regex | cfg;

lambda:
	| 'lambda' '->' expr
	| 'lambda' var (WHITESPACE var)* '->' expr
	| '(' lambda ')';

graph:
	| var
	| 'set_start' graph set
	| 'set_final' graph set
	| 'add_start' graph set
	| 'add_final' graph set
	| 'load' string;

set:
	| var
	| 'get_start' graph
	| 'get_final' graph
	| 'get_reachable' graph
	| 'get_edges' graph
	| 'get_labels' graph
	| 'get_vertices' graph
	| 'map' lambda set
	| 'filter' lambda set
	| '[' (expr (',' expr)*) ']'
	| '[' expr '..' expr ']'
	| '[' ']';

lang_binop: '&' | '|' | '.';
binop: '&&' | '||';
unop: 'not' | '-';

expr:
	| var
	| val
	| graph
	| set
	| expr lang_binop expr
	| expr '*'
	| expr binop expr
	| unop expr;

stmt: | 'print' expr | var '=' expr;
EOL: '\n';
prog: EOL* stmt (EOL+ stmt)* EOL* EOF;
