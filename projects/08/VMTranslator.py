from sys import argv
import os
import re
import pdb


def cleanup(raw_line):
    line = raw_line.replace(' ','') # Deletes white space
    if '//' in line: # Deletes comments
        line = line[:line.index('//') + 1]
        line = line.replace('/','')
    while '\\' in ('%r' % line):
        line = (line[:(('%r' % line).index('\\') - 1)] + 
                line[('%r' % line).index('\\'):]) 
    return line

def get_segment_type(line):
    val_index = re.search('\d', line)
    if 'function' in line or 'call' in line or 'return' in line:
        segment_type = 'function command'
    elif 'label' in line or 'goto' in line:
        segment_type = 'program flow'
    elif val_index is None:
        segment_type = 'operation'
    else:
        if 'pop' in line:
            seg_start = 3
        elif 'push' in line:
            seg_start = 4
        segment_type = line[seg_start:val_index.start()]
    return segment_type

def pass_through(raw_line):

    def write_function_command(line):
        global unique_id
        if line[:8] == 'function':
            arguments = int(line[-1])
            lines_to_write = ['(%s)' % line[8:-1]]
            for argument in range(1, arguments + 1):
                lines_to_write.extend(['@SP',
                                       'A=M',
                                       'M=0',
                                       '@SP',
                                       'M=M+1'])

            return lines_to_write

        elif line[:4] == 'call':
            arguments = int(line[-1])
            lines_to_write = ['@RET%s' % unique_id, # Push return-address
                              #'A=M', # Correct?  Omit?
                              'D=A', # Or D=M?
                              '@SP',
                              'A=M',
                              'M=D',
                              '@SP',
                              'M=M+1']
            for function_stack in ['LCL', 'ARG', 'THIS', 'THAT']:
                lines_to_write.extend(['@%s' % function_stack, # Push LCL, ARG,
                                       'D=M',                  # THIS, THAT
                                       '@SP',
                                       'A=M',
                                       'M=D',
                                       '@SP',
                                       'M=M+1'])
            lines_to_write.extend(['@%s' % arguments, # ARG = SP-n-5
                                   'D=A',
                                   '@5',
                                   'D=D+A',
                                   '@SP',
                                   'D=M-D',
                                   '@ARG',
                                   'M=D',
                                   '@SP', # LCL = SP
                                   'D=M',
                                   '@LCL',
                                   'M=D',
                                   '@%s' % line[4:-1], # goto F
                                   #'A=M', # Puts in infinite loop!  WHY?!
                                   '0;JMP',
                                   '(RET%s)' % unique_id]) # (return-address)
            unique_id += 1
            return lines_to_write

        elif line == 'return': # ARG is address, *ARG is value
            lines_to_write = ['@LCL', # Store address LCL in temp addy FRAME
                              'D=M',
                              '@FRAME%s' % unique_id,
                              'M=D',
                              '@5', # Addy RET is value of addy (FRAME - 5)
                              'A=D-A',
                              'D=M',
                              '@RET%s' % unique_id,
                              'M=D',
                              '@SP', # Value of ARG is pop(SP)
                              'M=M-1',
                              'A=M',
                              'D=M',
                              '@ARG',
                              'A=M',
                              'M=D',
                              '@ARG', # Addy SP is Addy ARG + 1
                              'D=M+1',
                              '@SP',
                              'M=D']
            n = 1
            for function_stack in ['THAT', 'THIS', 'ARG', 'LCL']:
                lines_to_write.extend(['@FRAME%s' % unique_id, # Addy FStk is
                                       'D=M',                # value of addy
                                       '@%d' % n,            # (FRAME - n)
                                       'A=D-A',
                                       'D=M',
                                       '@%s' % function_stack,
                                       'M=D'])
                n += 1
            lines_to_write.extend(['@RET%s' % unique_id,
                                   'A=M',
                                   '0;JMP'])
            unique_id += 1
            return lines_to_write

    def write_program_flow(line):
        if 'label' in line:
            return ['(%s)' % line[5:]]
        elif 'if-' in line:
            return ['@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@%s' % line[7:],
                    'D;JGT']
        else:
            return ['@%s' % line[4:],
                    'A=M',
                    '0;JMP']

    def write_pop(segment_type, val, RAM_loc):
        if segment_type == 'static':
            return ['@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@%s.%d' % (base_file_name, val),
                    'M=D']
        elif segment_type == 'temp' or segment_type == 'pointer':
            return ['@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@%s' % RAM_loc,
                    'M=D']
        else:
            return ['@%d' % val,
                    'D=A',
                    '@%s' % RAM_loc,
                    'A=M',
                    'D=D+A', # Where we want to push
                    '@SP', # Temp location
                    'A=M',
                    'M=D', # Temp now holds dest location
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@SP',
                    'A=M+1',
                    'A=M',
                    'M=D']


    def write_push(segment_type, val, RAM_loc):
        if segment_type == 'constant':
            return ['@%d' % val, # constants
                    'D=A',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1']
        elif segment_type == 'static':
            return ['@%s.%d' % (base_file_name, val),
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1']
        elif segment_type == 'temp' or segment_type == 'pointer':
            return ['@%s' % RAM_loc,
                    'D=M',
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1']
        else:
            return ['@%d' % val,
                    'D=A',
                    '@%s' % RAM_loc,
                    'D=D+M',
                    'A=D', # Where we want to get value
                    'D=M', # D is now number to push
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1']
    
    def write_operation(operation):
        global unique_id
        bi_command_list = {'ad':'+', 'su':'-', 'an':'&', 'or':'|'}
        un_command_list = {'ne':'-', 'no':'!'}
        comp_command_list = {'eq':'EQ', 'gt':'GT', 'lt':'LT'} 
        if operation in bi_command_list:
            lines_to_write = ['@SP',
                              'M=M-1',
                              'M=M-1',
                              'A=M',
                              'D=M',
                              '@SP',
                              'M=M+1',
                              'A=M',
                              'D=D%sM' % bi_command_list[operation],
                              '@SP',
                              'M=M-1',
                              'A=M',
                              'M=D',
                              '@SP',
                              'M=M+1']
        elif operation in comp_command_list: 
            lines_to_write =  ['@SP',
                              'M=M-1',
                              'M=M-1',
                              'A=M',
                              'D=M', # D = first operand
                              '@SP',
                              'M=M+1',
                              'A=M', # A = where second operand lives
                              'D=D-M', # D = difference btw operands
                              '@VMTRUE%s' % unique_id,
                              'D;J%s' % comp_command_list[operation],
                              'D=0',
                              '@VMLINE%s' % unique_id,
                              '0;JMP',
                              '(VMTRUE%s)' % unique_id,
                              'D=-1',
                              '(VMLINE%s)' % unique_id, # D is now result
                              '@SP',
                              'M=M-1',
                              'A=M',
                              'M=D',
                              '@SP',
                              'M=M+1']
            unique_id += 1
        else:
            lines_to_write = ['@SP',
                              'M=M-1',
                              'A=M',
                              'M=%sM' % un_command_list[operation],
                              '@SP',
                              'M=M+1']
        return lines_to_write
            

    segments = {'argument': 'ARG', 'local': 'LCL', 'this': 'THIS', 
                'that': 'THAT', 'constant': 'SP', 'temp': 5, 'pointer':3, 
                'static':16}
    RAM_loc = None
    lines_to_write = [] # Initizalize line to write to new .asm file.
    line = cleanup(raw_line)
    if line == '':
        return ''
    segment_type = get_segment_type(line)

    if segment_type == 'operation':
        operation = line[0:2]
        lines_to_write = write_operation(operation)

    elif segment_type == 'program flow':
        lines_to_write = write_program_flow(line)

    elif segment_type == 'function command':
        lines_to_write = write_function_command(line)

    else:
        RAM_loc = segments[segment_type]
        val_index = re.search('\d', line)
        val = int(line[val_index.start():])
        if segment_type == 'temp': 
            RAM_loc = 5 + val
        if segment_type == 'pointer':
            RAM_loc = 3 + val
        if 'pop' in line:
            lines_to_write = write_pop(segment_type, val, RAM_loc)
        if 'push' in line:
            lines_to_write = write_push(segment_type, val, RAM_loc)

    return lines_to_write


def write_init():
    lines_to_write = ['@256',
                      'D=A',
                      '@SP',
                      'M=D']
    lines_to_write.extend(pass_through('call Sys.init 0'))
    return lines_to_write

def write_to_asm(lines_to_write, asm):
    for line_to_write in lines_to_write:
        if line_to_write == '':
            continue
        asm.write(line_to_write + '\n')
    return

def get_asm_filename(vm_directory):
    slash_index = vm_directory.rfind('/')
    return vm_directory + '/' + vm_directory[slash_index + 1:] + '.asm'

def process_files(vm_directory):
    lines_to_write = write_init()
    asm_filename = open(get_asm_filename(vm_directory), 'w')
    for filename in os.listdir('%s' % vm_directory):
        if filename[-3:] == '.vm':
            vm_file = open(vm_directory + '/' + filename, 'r') 
            for raw_line in vm_file:
                lines_to_write.extend(pass_through(raw_line))
    write_to_asm(lines_to_write, asm_filename)
    vm_file.close()
    asm_filename.close()


if __name__ == '__main__':
    script, vm_directory = argv

    if vm_directory[-1] == '/':
        vm_directory = vm_directory[:-1] 

    unique_id = 0
    process_files(vm_directory) 
    

