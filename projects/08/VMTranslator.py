from sys import argv
import re



def cleanup(raw_line):
    line = raw_line.replace(' ','') # Deletes white space
    if '//' in line: # Deletes comments
        line = line[:line.index('//') + 1]
        line = line.replace('/','')
    while '\\' in ('%r' % line):
        line = (line[:(('%r' % line).index('\\') - 1)] + 
                line[('%r' % line).index('\\'):]) 
    return line

def write_to_asm(lines_to_write, asm):
    for line_to_write in lines_to_write:
        asm.write(line_to_write + '\n')
    return

def get_segment_type(line):
    val_index = re.search('\d', line)
    if val_index is None:
        segment_type = 'operation'
    else:
        if 'pop' in line:
            seg_start = 3
        elif 'push' in line:
            seg_start = 4
        segment_type = line[seg_start:val_index.start()]
    return segment_type

def pass_through(vm_file):

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
                    '@5', # Temp location
                    'M=D', # Temp now holds dest location
                    '@SP',
                    'M=M-1',
                    'A=M',
                    'D=M',
                    '@5',
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
            lines_to_write = ['(VMTRUE%s)' % vm_line,
                              'D=-1',
                              '@VMLINE%s' % vm_line,
                              '0;JMP',
                              '@SP',
                              'M=M-1',
                              'M=M-1',
                              'A=M',
                              'D=M', # D = first operand
                              '@SP',
                              'M=M+1',
                              'A=M', # A = where second operand lives
                              'D=D-M', # D = difference btw operands
                              '@VMTRUE%s' % vm_line,
                              'D;J%s' % comp_command_list[operation],
                              'D=0',
                              '(VMLINE%s)' % vm_line]
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
    base_file_index = vm_file.rfind('/') + 1
    base_file_name = str(vm_file[base_file_index:].replace('.vm', ''))
    new_file_name = vm_file.replace('vm', 'asm')
    asm = open(new_file_name, 'w') # asm is new '.asm' file.
    f = open(vm_file, 'r')
    vm_line = 0

    for raw_line in f:
    
        lines_to_write = [] # Initizalize line to write to new .asm file.
        line = cleanup(raw_line)
        if line == '':
            continue
        vm_line += 1
        segment_type = get_segment_type(line)

        if segment_type == 'operation':
            operation = line[0:2]
            lines_to_write = write_operation(operation)

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

        write_to_asm(lines_to_write, asm)

    f.close()
    asm.close()

if __name__ == '__main__':
    script, vm_file = argv

    pass_through(vm_file)

