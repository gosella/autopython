print('¡Hola mundo!')
2 + 2
1 / 0

if True:
    a = 1
    print('OK')
     
    c = 1
else:
    a = 2

s = """aaa
bbb
ccc
ddd"""

print(s)

## Imprimiendo

print()
print("¡Hola, mundo!")
print("¡Hola", "mundo!")
print("Valor:", 123)
print("Una cosa... ", end=""); print("lleva a la otra")
print(1, 2, 3, 4 , sep=" | ")


## Números

## Enteros

42
1 + 1
4 - 2
2 * 4
1 / 2
1 / 2.0
1 // 2.0
1 // 2
from __future__ import division
1 / 2
1 // 2
3 % 2
2 ** 4

0xff
0777
0o777
0b1010

type(1)

int()
int(2)
int('42')
int('1010', 2)
int('777', 8)
int('ff', 16)


## Enteros largos

2 ** 70
2L
2 + 2L

type(1L)

long()
long(2)
long('42')


## Reales en punto flotante

1.0
2.5
.5
4.
1.5e10
1E-15

1 + 1.0

0.4
n = 0.4
n
n == 0.4
print(n)
n
str(n)
repr(n)

type(1.0)

float()
float(10)
float('1.5')
float('3.14159265358979323846')


## Complejos

1 + 2j
4j
3.25 + 2.5j

type(1j)

complex()
complex(1, 2)

c1 = 3+4j
c1.real
c1.imag

c2 = 1-2j

c1 + c2
c1 - c2
c1 * c2
c1 / c2
c1 ** 2


## Booleanos (bool)

True
False

False == 0
True == 1
False == 1
True == 2
True + 1
False + 1

type(True)

bool()

bool(0)
bool(0L)
bool(0.0)
bool(0j)

bool('')
bool([])
bool(())
bool({})
bool(set())

bool(None)

bool(2)
bool(4.5)
bool(3j)
bool('Hola')
bool([1, 2, 3])
bool((4, 5))
bool({'a': 10})
bool(set([1, 2, 3]))

1 == 1
1 != 1
2 > 1
2 < 1
3 >= 1
2 <= 4
1 is 1
1 is not 2
True == 1
True is 1

True and True
True and False
False and False
True or True
True or False
False or False

1 and 2
1 or 2
0 and 2
0 or 2

not 0
not "Hola"
not ""

1 < 3 < 5
1 < 3 and 3 < 5

1 == 2 < 5
1 == 2 and 2 < 5


## Cadenas de bytes (str) - inmutables

'una cadena'
"otra cadena"

'Esta contiene "comillas dobles".'
"Esta contiene 'comillas simples'."

'''Una cadena
escrita en
varias líneas'''

print('''Una cadena
escrita en
varias líneas''')

"""Otra cadena
escrita en
varias líneas"""

'Usando...\n\tcódigos de \'escape\'.'
print('Usando...\n\tcódigos de \'escape\'.')

r'Una cadena raw ignora los códigos de escape (\n\t\r)'
r"Ejemplo: viejo\nuevo."

"abc" + "def"
'abcd' * 10
'-' * 80

s = 'Esto es una prueba'
len(s)

s[0]
s[1]

s[len(s)-1]
s[-1]
s[-2]

s[0] = 'e'

s[5:11]
s[12:]
s[:5]
s[:-7]
s[-10:-7]

s[0:11]
s[0:11:2]
s[0:11:3]
s[10:4]
s[10:4:-1]
s[::2]
s[::-1]

s = 'una CADENA'
s
s.lower()
s.upper()

s = 'backup-20100601.zip'
s.startswith('back')
s.endswith('.zip')

s = 'abcabcabcab'
s.count('bc')

s.find('cab')
s.find('cc')
s.rfind('cab')

s.index('cab')
s.index('cc')
s.rindex('cab')

s.replace('ca', '--')
s.replace('cc', '--')

s = 'esto es un texto de prueba'
lista = s.split()
lista
lista2 = s.split('o')
lista2

" ".join(lista)
"\n".join(lista)
print("\n".join(lista))


type('una cadena')

str()
str(1)
str(1L)
str(1.0)
str(1j)
str(True)
str(False)
str(None)
str([1, 2, 3])
str((1, 2, 3))
str({"clave": "valor"})
str(set((1, 2, 1, 2, 3)))
str('una cadena')


## Listas

[]
[1, 2, 3, 4]
[10, "Hola", [4, 8, 15, 16, 23, 42], 3.14]

lista1 = [1, 2, 3]
lista2 = [4, 5, 6]

lista1 + lista2
lista1 * 4
4 * lista1

lista2
lista2 += lista1
lista2

lista = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
len(lista)

lista[0]
lista[7]

lista[-1]
lista[-2]

lista[0] = '-A-'
lista
lista[-1] = '-H-'
lista

lista[2:5]
lista[::-1]

lista
lista[3:6]
lista[3:6] = ["-D-", "-E-", "-F-"]
lista
lista[2:4]
lista[2:4] = ["C", "CH", "D"]

lista
lista[3]
del lista[3]
lista
lista[5:]
del lista[5:]
lista
del lista[:2]
lista
del lista[:]
lista
del lista
lista


lista1 = [1, 2, 3]
lista2 = [1, 2, 3]
lista1 == lista2
lista1 != lista2

lista2 = [1, 4, 3]
lista1 == lista2
lista1 != lista2
lista1 < lista2
lista1 <= lista2
lista1 > lista2
lista1 >= lista2

lista = [1, 2, 3, 4, 'x']
2 in lista
'x' in lista
42 in lista
42 not in lista


type(lista)

list()
list( [1, 2, 3] )
list( "Hola" )


lista = []
lista.append('a')
lista
lista.append('b')
lista

lista.insert(0, 'inicio')
lista
lista.insert(2, 'medio')
lista
lista.insert(5, 'fin')
lista
lista.insert(15, 'fin')
lista

lista.extend([1, 2, 3])
lista
lista += [4, 5, 6]
lista

lista.remove('fin')
lista
lista.remove(42)
lista
lista.pop()
lista
lista.pop()
lista

lista.append('fin')
lista

lista.count('fin')
lista.index('fin')

lista
lista.reverse()
lista

lista = [4, 1, 6, 9, 1, 8, 2, 7, 3, 5]
lista.sort()
lista

lista.sort(reverse=True)
lista


## Tuplas (tuple)

(1, 2, 3, 4)
()
(1)
(1, )
(
 1, 2, 
 3, 4,
)
(10, "Hola", [4, 8, 15, 16, 23, 42], 3.14)

tupla1 = (1, 2, 3)
tupla2 = (4, 5, 6)
tupla1 + tupla2
tupla1 * 3

tupla = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
len(tupla)

tupla[0]
tupla[-1]
tupla[2:5]

tupla[0] = 'X'
tupla[3]
del tupla[3]

tupla1 = (1, 2, 3)
tupla2 = (1, 4, 3)
tupla1 < tupla2

tupla = (1, 2, 3, 4, )
2 in tupla
'x' not in tupla

type(tupla)

tuple()
tuple( [1, 2, 3] )

# asda
