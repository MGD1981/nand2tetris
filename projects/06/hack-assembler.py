#! /usr/bin/python
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

    symbol_table = {'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4,
                    'R0':0, 'R1':1, 'R2':2, 'R3':3, 'R4':4, 'R5':5, 'R6':6,
                    'R7':7, 'R8':8, 'R9':9, 'R10':10, 'R11':11, 'R12':12,
                    'R13':13, 'R14':14, 'R15':15, 'SCREEN':16384, 'KBD':24576}

    line_number = -1
    f = open(hack_file, 'r') 
    for line in f:
        line = cleanup(line)
        if line == '':
            continue
        if '@' in line or '=' in line or ';' in line:
            line_number += 1

        if line[0] == '(':
            eol = line.index(')')
            address_label = line[1:eol]
            symbol_table[address_label] = line_number + 1
    f.close()

    return symbol_table


def run_assembler_pass(hack_file, symbol_table):
    new_file_name = hack_file.replace('asm', 'hack')
    h = open(new_file_name, 'w') # h is new '.hack' file
    f = open(hack_file, 'r')
    ram = 16
    
    def determine_line_type(line):
        eol = find_eol(line)
        if '@' in line:
            if line[line.index('@')+1:eol].isdigit():
                return "address load by location"
            else:
                return "address load by symbol"
        if ';J' in line:
            return "jump command"
        if '=' in line:
            return "computation"
        else:
            return "garbage"

    def c_code(line):
        a = '0'
        c = None
        eol = find_eol(line)
        loc = 0
        if '=' in line:
            loc = line.index('=') + 1
        comp = line[loc:eol]

        if 'M' in comp:
            a = '1'
        if comp == '0':
            c = '101010'
        elif comp == '1':
            c = '111111'
        elif comp == '-1':
            c = '111010'
        elif comp == 'D':
            c = '001100'
        elif comp == 'A' or comp == 'M':
            c = '110000'
        elif comp == '!D':
            c = '001101'
        elif comp == '!A' or comp == '!M':
            c = '110001'
        elif comp == '-D':
            c = '001111'
        elif comp == '-A' or comp == '-M':
            c = '110011'
        elif comp == 'D+1':
            c = '011111'
        elif comp == 'A+1' or comp == 'M+1':
            c = '110111'
        elif comp == 'D-1':
            c = '001110'
        elif comp == 'A-1' or comp == 'M-1':
            c = '110010'
        elif comp == 'D+A' or comp == 'D+M':
            c = '000010'
        elif comp == 'D-A' or comp == 'D-M':
            c = '010011'
        elif comp == 'A-D' or comp == 'M-D':
            c = '000111'
        elif comp == 'D&A' or comp == 'D&M':
            c = '000000'
        elif comp == 'D|A' or comp == 'D|M':
            c = '010101'
        return a + c


    def d_code(line):
        d0 = '0'
        d1 = '0'
        d2 = '0'
        loc = line.index('=')
        if 'A' in line[:loc]:
            d0 = '1'
        if 'D' in line[:loc]:
            d1 = '1'
        if 'M' in line[:loc]:
            d2 = '1'
        return d0 + d1 + d2

    def j_code(line):
        loc = line.index(';J') 
        j_abbrev = line[loc+2:loc+4]
        if j_abbrev == 'GT': j = '001'
        elif j_abbrev == 'EQ': j = '010'
        elif j_abbrev == 'GE': j = '011'
        elif j_abbrev == 'LT': j = '100'
        elif j_abbrev == 'NE': j = '101'
        elif j_abbrev == 'LE': j = '110'
        elif j_abbrev == 'MP': j = '111'
        return j 


    for line in f:

        # Line initialization
        ignore = False
        i = '111'
        d = '000' 
        j = '000'
        line = cleanup(line)
        if line == '':
            continue
        loc = 0
        line_type = determine_line_type(line)

        if line_type == "garbage": 
            continue

        if line_type[:12] == "address load": # Writes the address to h
            eol = find_eol(line)
            address_label = line[loc+1:eol]
            if line_type == "address load by symbol":
                if address_label not in symbol_table:
                    symbol_table[address_label] = ram
                    ram += 1
                address = symbol_table[address_label]
            if line_type == "address load by location": 
                address = int(address_label)
            if address >= 32768:
                print "Error: address larger than 15 bits!"
                f.close()
                break
            bin_address_uf = bin(address)
            bin_address = bin_address_uf[2:]
            extra_0s = 16 - len(bin_address)
            readable_address = '0' * extra_0s + bin_address
            h.write(readable_address + '\n')
            continue
            loc = len(line)-1

        if line_type == "jump command":
            j = j_code(line)

        if line_type == "computation": # Write the instruction to h
            d = d_code(line)

        ac = c_code(line)

        newline = i + ac + d + j + '\n' 
        h.write(newline)

    h.close()
    f.close()



if __name__ == '__main__':
    script, hack_file = argv

    symbol_table = run_symbol_pass(hack_file)
    run_assembler_pass(hack_file, symbol_table)

