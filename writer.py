import sys
import time

if len(sys.argv)>1:
    filename = sys.argv[1]
    file = open(filename, 'w')
    temp=0
    while(temp<=100):
        text = file.write('a')
        time.sleep(0.1)
        temp+=1
    file.close()
