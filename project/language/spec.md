# Задача 12. Язык запросов к графам

## Описание абстрактного синтаксиса языка

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Int of int
  | Bool of bool
  | Regex of regex
  | CFG of cfg

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda =
    Lambda of List<var> * expr
```

## Описание конкретного синтаксиса

```
whitespace := [ \t\r]+ -> skip
char := [a-z] | [A-Z]
digit := [0-9]
nonzero_digit := [1-9]
id = char (char | digit)*

var := id

string := '"' (char | digit | '_')* '"'
symbol := char | digt | '_' | '*' | '+' | '.'
int := nonzero_digit digit+
bool := 'true' | 'false'
regex := '/' symbol* '/'
cfg := 'g' '/' symbol* '/'

val := string | int | bool | regex | cfg

lambda :=
  | 'lambda' '->' expr
  | 'lambda' var (whitespace var)* '->' expr

path := '"' (char | digit | '_' | '/' | '.')* '"'

graph :=
  | var
  | 'set_start' graph set
  | 'set_final' graph set
  | 'add_start' graph set
  | 'add_final' graph set
  | 'load' path

set :=
  | var
  | 'get_start' graph
  | 'get_final' graph
  | 'get_reachable' graph
  | 'get_edges' graph
  | 'get_labels' graph
  | 'get_vertices' graph
  | 'map' lambda set
  | 'filter' lambda set
  | '[' (expr (',' expr)*)? ']'
  | '[' expr '..' expr ']'

lang_binop := '&' | '|' | '.'
binop := '&&' | '||'
unop := 'not' | '-'

expr :=
  | var
  | val
  | graph
  | set
  | expr lang_binop expr
  | expr '*'
  | expr binop expr
  | unop expr

stmt :=
  | 'print' expr
  | var '=' expr

prog := (stmt ('\n'+ stmt)*)? EOF

```

## Пример

В этом примере загружается граф pizza, отмечаются стартовые и конечные вершины, и граф пересекается с регулярным выражением `l1 | l2 | (l3 . l2)*`, а также с грамматикой `S -> epsilon | aS`.

```
graph = load "pizza"
regex = /l1 | l2 | (l3 . l2)*/
cfg = g/S -> epsilon | aS/

graph_vertices = get_vertices graph
graph = set_start graph graph_vertices
graph = set_final graph [2..10]

result1 = graph & regex
result2 = graph & cfg

print result1
print result2
```
