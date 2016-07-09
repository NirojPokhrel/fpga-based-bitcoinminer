#This script will create two ports one can be used for writing and another for reading or something like that.
#You can study more about it for further understanding.
socat -d -d pty,raw,echo=0 pty,raw,echo=0