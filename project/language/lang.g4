grammar lang;

WHITESPACE: [ \t\r] -> skip;
CHAR: [a-z] | [A-Z] | '_';
DIGIT: [0-9];
NONZERO: [1-9];

val: string | int | bool | regex | cfg;

STRING: '"' (CHAR | DIGIT | '_' | '/' | '.')* '"';
INT: NONZERO DIGIT*;
BOOL: 'true' | 'false';
REGEX: '/' ~[\n]* '/';
CFG: 'g' '/' ~[\n]* '/';

var: CHAR | ID;
ID: CHAR (CHAR | DIGIT)*;

string: STRING;
int: DIGIT | INT;
bool: BOOL;
regex: REGEX;
cfg: CFG;

lambda:
	| 'lambda' '->' expr
	| 'lambda' var+ '->' expr
	| '(' lambda ')';

graph:
	| var
	| set_start
	| set_final
	| add_start
	| add_final
	| load;

set_start: 'set_start' graph set;
set_final: 'set_final' graph set;
add_start: 'add_start' graph set;
add_final: 'add_final' graph set;
load: 'load' string;
PATH: '"' (CHAR | DIGIT | '/' | '.')* '"';

set:
	| var
	| get_start
	| get_final
	| get_reachable
	| get_edges
	| get_labels
	| get_vertices
	| map
	| filter
	| list
	| range;

get_start: 'get_start' graph;
get_final: 'get_final' graph;
get_reachable: 'get_reachable' graph;
get_edges: 'get_edges' graph;
get_labels: 'get_labels' graph;
get_vertices: 'get_vertices' graph;
map: 'map' lambda set;
filter: 'filter' lambda set;
list: empty_list | '[' (expr (',' expr)*) ']';
empty_list: '[' ']';
range: '[' expr '..' expr ']';

LANG_AND: '&';
LANG_OR: '|';
LANG_DOT: '.';
lang_binop: LANG_AND | LANG_OR | LANG_DOT;

AND: '&&';
OR: '||';
binop: AND | OR;

NOT: 'not';
NEG: '-';
unop: NOT | NEG;

KLEENE: '*';

expr:
	| var
	| val
	| graph
	| set
	| expr LANG_AND expr
	| expr LANG_OR expr
	| expr LANG_DOT expr
	| expr KLEENE
	| expr AND expr
	| expr OR expr
	| NOT expr
	| NEG expr;

stmt: | print | bind;
bind: var '=' expr;
print: 'print' expr;
EOL: '\n';
prog: EOL* stmt (EOL+ stmt)* EOL* EOF;
