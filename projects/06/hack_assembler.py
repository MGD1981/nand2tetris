#! /usr/local/bin/python
from sys import argv
import pdb

def cleanup(line):
    loc = 0
    line = line.replace(' ','') # Deletes white space
    if '//' in line: # Deletes comments
        loc = line.index('//') - 1
        line = line[:loc+2]
        line = line.replace('/','')
    return line 

def find_eol(line):
    cline = line.replace('\n','').replace('\r','')
    eol = len(cline) 
    if ';' in line:
        eol = line.index(';')
    return eol 

def run_symbol_pass(hack_file):
    #pdb.set_trace()


    symbol_table = {'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4,
                    'R0':0, 'R1':1, 'R2':2, 'R3':3, 'R4':4, 'R5':5, 'R6':6, 'R7':7,
                    'R8':8, 'R9':9, 'R10':10, 'R11':11, 'R12':12, 'R13':13,
                    'R14':14, 'R15':15, 'SCREEN':16384, 'KBD':24576}

    # First Run-Through
    line_number = -1
    s = open(hack_file, 'r') # s is copy file for first pass
    for line in s:
        line = cleanup(line)
        if line == '':
            continue
        loc = 0
        if '@' in line or '=' in line or ';' in line:
            line_number += 1

        if line[loc] == '(':
            eol = line.index(')')
            address_label = line[loc+1:eol]
            symbol_table[address_label] = line_number + 1
    s.close()

    ram = 16
    s = open(hack_file, 'r') # s is copy file for first pass
    for line in s:
        line = cleanup(line)
        if line == '':
            continue
        loc = 0
        if line[loc] == '@':
            eol = find_eol(line) 
            address_label = line[loc+1:eol]
            if address_label not in symbol_table and not address_label.isdigit():
                symbol_table[address_label] = ram
                ram = ram + 1

    return symbol_table

def run_assembler_pass(hack_file, symbol_table):
    h = open(hack_file[0:len(hack_file)-4] + '.hack2', 'w') # h is new '.hack' file
    f = open(hack_file, 'r') # f is original file
    # Second Run-Through
    for line in f:
        ignore = False
        i = [1,1,1]
        a = [0]
        c = [0,0,0,0,0,0]
        d = [0,0,0]
        j = [0,0,0]
        line = cleanup(line)
        if line == '':
            continue
        loc = 0
        if ('@' not in line and '=' not in line and
            ';' not in line):
            ignore = True
        if line[loc] == '@': # Writes the address to h
            eol = find_eol(line)
            try:
                address = int(line[loc+1:eol])
            except ValueError:
                address = line[loc+1:eol]
                if address not in symbol_table:
                    pdb.set_trace()
                    print "Error: symbol not defined!  ", address
                    f.close()
                    break
                address = symbol_table[address]            
            if address >= 32768:
                print "Error: address larger than 15 bits!"
                f.close()
                break
            address = bin(address)
            address = address[2:]
            extra_0s = 16 - len(address)
            address = '0' * extra_0s + address
            h.write(address + '\n')
            ignore = True
            loc = len(line)-1

        if ';J' in line:
            loc = line.index(';J') 
            j_code = line[loc+2:loc+4]
            if j_code == 'GT': j = [0,0,1]
            elif j_code == 'EQ': j = [0,1,0]
            elif j_code == 'GE': j = [0,1,1]
            elif j_code == 'LT': j = [1,0,0]
            elif j_code == 'NE': j = [1,0,1]
            elif j_code == 'LE': j = [1,1,0]
            elif j_code == 'MP': j = [1,1,1]
            loc = 0

        if '=' in line: # Write the instruction to h
            loc = line.index('=')
            if 'A' in line[:loc]:
                d[0] = 1
            if 'D' in line[:loc]:
                d[1] = 1
            if 'M' in line[:loc]:
                d[2] = 1
            loc += 1
        eol = find_eol(line)  
        comp = line[loc:eol]
        if 'M' in comp:
            a = 1
        if comp == '0':
            c = [1,0,1,0,1,0]
        elif comp == '1':
            c = [1,1,1,1,1,1]
        elif comp == '-1':
            c = [1,1,1,0,1,0]
        elif comp == 'D':
            c = [0,0,1,1,0,0]
        elif comp == 'A' or comp == 'M':
            c = [1,1,0,0,0,0]
        elif comp == '!D':
            c = [0,0,1,1,0,1]
        elif comp == '!A' or comp == '!M':
            c = [1,1,0,0,0,1]
        elif comp == '-D':
            c = [0,0,1,1,1,1]
        elif comp == '-A' or comp == '-M':
            c = [1,1,0,0,1,1]
        elif comp == 'D+1':
            c = [0,1,1,1,1,1]
        elif comp == 'A+1' or comp == 'M+1':
            c = [1,1,0,1,1,1]
        elif comp == 'D-1':
            c = [0,0,1,1,1,0]
        elif comp == 'A-1' or comp == 'M-1':
            c = [1,1,0,0,1,0]
        elif comp == 'D+A' or comp == 'D+M':
            c = [0,0,0,0,1,0]
        elif comp == 'D-A' or comp == 'D-M':
            c = [0,1,0,0,1,1]
        elif comp == 'A-D' or comp == 'M-D':
            c = [0,0,0,1,1,1]
        elif comp == 'D&A' or comp == 'D&M':
            c = [0,0,0,0,0,0]
        elif comp == 'D|A' or comp == 'D|M':
            c = [0,1,0,1,0,1]


        newline = []
        newline.append(i)
        newline.append(a)
        newline.append(c)
        newline.append(d)
        newline.append(j)
        newline = str(newline)
        newline = (newline.replace('[','').replace(']','').replace(
                   ',','').replace(' ',''))
        if not ignore: 
            h.write(newline + '\n')

    h.close()
    f.close()



if __name__ == '__main__':
    script, hack_file = argv

    symbol_table = run_symbol_pass(hack_file)
    run_assembler_pass(hack_file, symbol_table)
