ok = False

if 1 < 10:
	a = 1
	b = 2
	c = 3
	t = a
	a = b
	b = c
	'This is a very long string just for filling a complete line and more, to see how well does pagination deals with it...'
	c = t
	t = c
	c = b
	b = a
	a = t
	assert a == 1
	assert b == 2
	assert c == 3
	ok = True
	print(a)
	print(b)
	print(c)
	2 == 5
	'WTF? Is this really working as expected? Wow... It must be the product of long hours of hard labor iron out all the bugs than may or may not plage this awesome tool. :-)'
	ok = False
	ok = True
	ok = False / True
	'Oh well..'
	ok = True / True
	ok = False + True
	ok = True + False
	ok = False * False
	ok = not ok

print(ok)