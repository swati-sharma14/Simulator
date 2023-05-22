from sys import stdin
from sys import exit


#############################################################
# General purpose:

def find_instrn(opc):
    if (opc in instrns.keys()):
        return instrns[opc]
    print("Invalid opcode")
    print('Line number:',i+1)
    exit()

def find_reg(addr):
    if (addr in registers.keys()):
        return registers[addr]
    print('Invalid register address')
    print('Line number:',i+1)
    exit()

def find_type(inst):
    for i in range(len(types)):
        if(inst in types[i]):
            return i+1

def getval(addr):
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

def movi(reg,immval):
    registers[reg] = 8*'0' + dectobin(immval)[8:]

def ls(reg,immval):
    newreg = registers[reg][immval:]
    registers[reg] = newreg + (16-len(newreg))*'0'

def rs(reg,immval):
    newreg = immval*'0' + registers[reg]
    registers[reg] = newreg[:16]

#############################################################
# Type C

def mov(rs,rd):
    registers[rd] = registers[rs]

def div(num,den):
    registers['000'] = dectobin(int(num/den))
    registers['001'] = dectobin(num%den)

def bitnot(rs,rd):
    out = ""
    for i in range(16):
        out = out+str(1 - int(registers[rs][i]))
    registers[rd] = out

def comp(r1,r2):
    if(r1==r2):
        x = '001'
    elif(r1>r2):
        x = '010'
    else:
        x = '100'
    registers['111'] = '0'*12 + registers['111'][12] + x

#############################################################
# Type D

def ld(reg,addr):
    if(bintodec(addr)<n):
        print('Trying to load instruction memory in register')
        print('Line number:',i+1)
        exit()
    registers[reg] = getval(addr)

def st(reg,addr):
    a = bintodec(addr)
    if(a<n):
        print('Trying to store value to instruction memory')
        print('Line number:',i+1)
        exit()
    memory[a] = registers[reg]

#############################################################
# Type E

def jmp(pc,addr):
    return addr

def jlt(pc,addr):
    if(registers['111'][-3]==1):
        return addr
    else:
        return pc

def jgt(pc,addr):
    if(registers['111'][-2]==1):
        return addr
    else:
        return pc

def je(pc,addr):
    if(registers['111'][-1]==1):
        return addr
    else:
        return pc

#############################################################
# Type F

def hlt():
    return

#############################################################
# Print pc

def print_pc(pc):
    print(dectobin(pc)[8:], end = "  ")

#############################################################
# Print registers

def print_regs(regs):
    for r in regs.keys():
        print(regs[r], end = "  ")
    print()

#############################################################
# Print memory

def print_memory(mem):
    for line in mem:
        print(line)
    print()

#############################################################
# Data sets

instrns = {'10000':add,'10001':sub,'10010':movi,'10011':mov,'10100':ld,'10101':st,'10110':mul,'10111':div,'11000':rs,'11001':ls,'11010':xor,'11011':bitor,'11100':bitand,'11101':bitnot,'11110':comp,'11111':jmp,'01100':jlt,'01101':jgt,'01111':je,'01010':hlt}
registers = {'000':dectobin(0),'001':dectobin(0),'010':dectobin(0),'011':dectobin(0),'100':dectobin(0),'101':dectobin(0),'110':dectobin(0),'111':dectobin(0)}
memory = [dectobin(0)]*256
types = [[add,sub,mul,xor,bitor,bitand],[movi,ls,rs],[mov,div,bitnot,comp],[ld,st],[jmp,jlt,je,jgt],[hlt]]

#############################################################
# Execution

n=0
for line in stdin:
    if(line[-1]=='\n'):
        memory[n] = line[:len(line)-1]
    else:
        memory[n] = line
    n+=1

pc = 0
for i in range(n):
    instrn = getval(dectobin(pc)[8:])
    func = find_instrn(instrn[:5])
    t = find_type(func)

    if(t==1):
        op1 = find_reg(instrn[7:10])
        op2 = find_reg(instrn[10:13])
        res = func(op1,op2)
        if(res==-1):
            registers[instrn[13:]] = dectobin(0)
            registers['111'] = '0'*12 + '1000'
        elif(len(res)>16):
            registers[instrn[13:]] = res[:16]
            registers['111'] = '0'*12 + '1000'
        else:
            registers[instrn[13:]] = res

    elif(t==2):
        reg = instrn[5:8]
        immval = bintodec(instrn[8:])
        func(reg,immval)

    elif(t==3):
        r1 = instrn[10:13]
        r2 = instrn[13:]
        func(r1,r2)

    elif(t==4):
        reg = instrn[5:8]
        addr = instrn[8:]
        func(reg,addr)

    elif(t==5):
        pc = func(pc,instrn[8:])
    
    elif(t==6):
        func()
        print_pc(pc)
        print_regs(registers)
        print()
        break

    print_pc(pc)
    print_regs(registers)
    print()

    pc = pc+1

print_memory(memory)

#############################################################
