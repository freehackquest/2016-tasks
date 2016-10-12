import hashlib 
import re
text = 'some message'

#formatKey:YearMonthDayHourMinutesSeconds
#OnlyNumbers
print('give me a key')
Key = input()

data = hashlib.sha256(Key.encode()).hexdigest()
	
for i in data:
	result = re.findall('\d', data) 
	s = ' '.join([str(i) for i in result])
	s = s.replace(' ', '')
	lenght = len(s)
	EM = s[0:lenght -2:] 

for i in text:
	m = ord(i)
	r = 0
	for r in range(0,len(text)):
		q = int(EM[r:r+2:])
		mes = q + m
		
		if mes > 128:
			les = mes - 128
			les = chr(les)
			r += 2
	les = ":".join("{:02x}".format(ord(c)) for c in les)
	print (les)	

