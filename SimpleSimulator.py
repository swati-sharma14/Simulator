from sys import stdin
from sys import exit
import fontTools
import matplotlib.pyplot as matplt
import numpy

#############################################################
# General purpose:

def find_instrn(opc):
    if (opc in instrns.keys()):
        return instrns[opc]
    print("Invalid opcode")
    print('Line number:',pc+1)
    exit()

def find_reg(addr):
    if (addr in registers.keys()):
        return registers[addr]
    print('Invalid register address')
    print('Line number:',pc+1)
    exit()

def find_type(inst):
    for i in range(len(types)):
        if(inst in types[i]):
            return i+1

def getval(addr):
    if(memory[bintodec(addr)]==''): return 16*'0'
    return memory[bintodec(addr)]

def dectobin(n):
    L=[]
    while(n!=0):
        temp=n%2 
        L.append(str(temp))
        n=n//2
    L.reverse()
    final = ''.join(L)
    if(len(final)>16):
        print('Invalid immediate value')
        exit()
    while(len(final)<16):
        final = '0' + final
    return final

def bintodec(string):
    n = 0
    x = 0
    while(len(string)>0):
        n+=(2**x)*int(string[-1])
        x+=1
        string = string[:len(string)-1]
    return n 

def floattobin(n):
    wh, decimal = str(n).split(".")
    
    wh = int(wh)
    whole = ''
    while(wh>0):
        whole = str(wh%2) + whole
        wh = wh//2
    whole = whole[1:]
    
    exponent = ''
    w = len(whole)
    while(w>0):
        exponent = str(w%2) + exponent
        w = w//2

    if(len(exponent)>3):
        print("Exponent exceeds 3 bits")
        print('Line number:',pc+1)
        exit()
    
    exponent = (3-len(exponent))*'0' + exponent

    decimal = int(decimal)/(10**len(decimal))

    mantissa = ''
    l = [0,1]
    while((decimal not in l) and len(mantissa)<(5-len(whole))):
        l.append(decimal)
        mantissa += str(int(decimal*2))
        decimal = (decimal*2)%1

    if(decimal not in l):
        registers['111'] = 12*'0' + '1' + registers['111'][13:]
        return 16*'0'

    mantissa = whole + mantissa
    if(len(mantissa)<5):
        mantissa = mantissa + (5-len(mantissa))*'0'

    return 8*'0' + exponent + mantissa

def bintofloat(n):
    exponent=bintodec(n[:3])
    if(exponent>5):
        beforedec = bintodec('1'+ n[3:] + (exponent-5)*'0')
    else:
        beforedec = bintodec('1' + n[3:exponent+3])

    afterdec=0
    right = n[3:][exponent:]
    
    for i in range(len(right)):
        j= -1*(i+1)
        afterdec += ((2**(j))*(int(right[i])))

    return beforedec + afterdec

#############################################################
# Type A

def add(a,b):
    a = bintodec(a)
    b = bintodec(b)
    return dectobin(a+b)

def sub(a,b):
    a = bintodec(a)
    b = bintodec(b)
    if(a>=b):
        return dectobin(a-b)
    else:
        return -1

def mul(a,b):
    a = bintodec(a)
    b = bintodec(b)
    return dectobin(a*b)

def addf(a,b):
    a = bintofloat(a[8:])
    b = bintofloat(b[8:])
    c = a+b
    if(c>252):
        registers['111'] = 12*'0' + '1' + registers['111'][13:]
        return 8*'0' + 8*'1'
    return floattobin(str(c))

def subf(a,b):
    a = bintofloat(a[8:])
    b = bintofloat(b[8:])
    c = a-b
    if(c>=0):
        return floattobin(str(c))
    else:
        return -1

def xor(a,b):
    out = ""
    for i in range(len(a)):
        out = out + str((int(a[i]) + int(b[i]))%2)
    return out

def bitor(a,b):
    out = ""
    for i in range(len(a)):
        if(a[i]=='1' or b[i]=='1'):
            out = out + '1'
        else:
            out = out + '0'
    return out

def bitand(a,b):
    out = ""
    for i in range(len(a)):
        out = out + str(int(a[i])*int(b[i]))
    return out

#############################################################
# Type B

def movf(reg,immval):
    registers[reg] = 8*'0' + immval

def movi(reg,immval):
    registers[reg] = 8*'0' + immval

def ls(reg,immval):
    newreg = registers[reg][bintodec(immval):]
    registers[reg] = newreg + (16-len(newreg))*'0'

def rs(reg,immval):
    newreg = bintodec(immval)*'0' + registers[reg]
    registers[reg] = newreg[:16]

#############################################################
# Type C

def mov(rs,rd):
    registers[rd] = registers[rs]

def div(r1,r2):
    num = bintodec(registers[r1])
    den = bintodec(registers[r2])
    registers['000'] = dectobin(int(num/den))
    registers['001'] = dectobin(num%den)

def bitnot(rs,rd):
    out = ""
    for i in range(16):
        out = out+str(1 - int(registers[rs][i]))
    registers[rd] = out

def comp(r1,r2):
    a = bintodec(registers[r1])
    b = bintodec(registers[r2])
    if(a==b):
        x = '001'
    elif(a>b):
        x = '010'
    else:
        x = '100'
    registers['111'] = '0'*12 + registers['111'][12] + x

#############################################################
# Type D

def ld(reg,addr):
    registers[reg] = getval(addr)

def st(reg,addr):
    memory[bintodec(addr)] = registers[reg]

#############################################################
# Type E

def jmp(pc,addr):
    y.append(bintodec(addr))
    return bintodec(addr) - 1

def jlt(pc,addr):
    if(registers['111'][-3]=='1'):
        y.append(bintodec(addr))
        return bintodec(addr) - 1
    else:
        return pc

def jgt(pc,addr):
    if(registers['111'][-2]=='1'):
        y.append(bintodec(addr))
        return bintodec(addr) - 1
    else:
        return pc

def je(pc,addr):
    if(registers['111'][-1]=='1'):
        y.append(bintodec(addr))
        return bintodec(addr) - 1
    else:
        return pc

#############################################################
# Type F

def hlt():
    return

#############################################################
# Append output at current instruction

def add_out(pc,regs,out):
    out.append(dectobin(pc)[8:])
    out[-1] = out[-1] + ' ' + ' '.join(regs.values())

#############################################################
# Print memory

def print_memory(mem):
    for line in mem:
        print(line)
    print()

#############################################################
# Print final output

def print_output(out):
    for i in range(len(out)):
        print(out[i])

#############################################################
# Data sets

instrns = {'10000':add,'10001':sub,'00000':addf,'00001':subf,'10010':movi,'10011':mov,'00010':movf,'10100':ld,'10101':st,'10110':mul,'10111':div,'11000':rs,'11001':ls,'11010':xor,'11011':bitor,'11100':bitand,'11101':bitnot,'11110':comp,'11111':jmp,'01100':jlt,'01101':jgt,'01111':je,'01010':hlt}
registers = {'000':16*'0','001':16*'0','010':16*'0','011':16*'0','100':16*'0','101':16*'0','110':16*'0','111':16*'0'}
memory = [16*'0']*256
types = [[add,sub,addf,subf,mul,xor,bitor,bitand],[movi,movf,ls,rs],[mov,div,bitnot,comp],[ld,st],[jmp,jlt,je,jgt],[hlt]]

#############################################################
# Execution

n=0
for line in stdin:
    if(n==256):
        print('Memory Limit Exceeded')
        exit()
    if(line[-1]=='\n'):
        memory[n] = line[:len(line)-1]
    else:
        memory[n] = line
    n+=1

pc = 0
out = []
graph_y = 0

while(pc!=n):
    graph_y += 1
    y = []
    curr = pc
    y.append(pc)
    instrn = getval(dectobin(pc)[8:])
    func = find_instrn(instrn[:5])
    t = find_type(func)

    if(t==1):
        op1 = find_reg(instrn[7:10])
        op2 = find_reg(instrn[10:13])
        res = func(op1,op2)
        if(res==-1):
            registers[instrn[13:]] = 16*'0'
            registers['111'] = '0'*12 + '1000'
        elif(len(res)>16):
            registers[instrn[13:]] = res[:16]
            registers['111'] = '0'*12 + '1000'
        else:
            registers[instrn[13:]] = res

    elif(t==2):
        reg = instrn[5:8]
        immval = instrn[8:]
        func(reg,immval)

    elif(t==3):
        r1 = instrn[10:13]
        r2 = instrn[13:]
        func(r1,r2)

    elif(t==4):
        reg = instrn[5:8]
        addr = instrn[8:]
        y.append(bintodec(addr))
        func(reg,addr)

    elif(t==5):
        pc = func(pc,instrn[8:])
        registers['111'] = 16*'0'
    
    elif(t==6):
        func()
        add_out(curr,registers,out)
        for j in range (len(y)):
            matplt.scatter(graph_y-1,y[j],color='red',s=13)
        break

    add_out(curr,registers,out)

    pc = pc+1

    for j in range (len(y)):
        matplt.scatter(graph_y-1,y[j],color='red',s=13)

print_output(out)

print_memory(memory)

#############################################################
# Plotting memory vs cycle graph

# mem_addr = range(0,264,8)
# matplt.yticks(mem_addr,fontsize=7)
# matplt.xticks(numpy.arange(0,graph_y,step=5),fontsize=6)
# matplt.ylabel('Memory address (in decimal)')
# matplt.xlabel('Cycle number')
# matplt.savefig('out')
#############################################################
