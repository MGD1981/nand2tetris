from sys import argv
import re
 

class HackNumber(object):
    """HackNumbers have unsigned 16-bit binary attributes and bitwise functions.
    """

    def __init__(self, dec_value):
        self.dec_value = dec_value
        self._out_of_bounds_test(dec_value)
        self.bin_array = self.dec_to_bin_array(dec_value)
        self.bin_string = ''.join(self.bin_array)
        if dec_value < 0:
            self.unsigned_value = self.find_complement(dec_value)
        else:
            self.unsigned_value = self.dec_value

    def _out_of_bounds_test(self, dec_value):
        if dec_value > 32767 or dec_value < -32768:
            raise TypeError("Value out of bounds for HackNumber object.")
        else:
            return

    def dec_to_bin_array(self, dec_number):
        if dec_number < 0:
            _number_to_convert = self.find_complement(dec_number)
        else:
            _number_to_convert = dec_number
        _bin_number_unformatted = bin(_number_to_convert)
        _bin_number_string = _bin_number_unformatted[2:]
        return self._bit_string_to_array(_bin_number_string)

    def find_complement(self, dec_number):
        if dec_number < 0:
            return 65536 + dec_number
        elif dec_number > 32767:
            return dec_number - 65536
        else:
            raise TypeError("Function only accepts negative numbers", 
                            "in base 10.")

    def _append_0s(self, bit_array):
        _extra_0s = 16 - len(bit_array)
        _extra_0_array = []
        for i in range(0, _extra_0s):
            _extra_0_array.append('0')
        return _extra_0_array + bit_array

    def _bit_string_to_dec(self, bit_string):
        bin_to_convert = eval("0b"+bit_string)
        new_dec = int(bin_to_convert)
        if bit_string[0] == '1':
            new_dec = self.find_complement(new_dec)
        return new_dec
        

    def _bit_string_to_array(self, _bin_number_string):
        bit_array = []
        for digit in _bin_number_string:
            bit_array.append(digit)
        bit_array = self._append_0s(bit_array)
        return bit_array
            
    def bitand(self, hack_number2):
        result_array = []
        for i in range(0,16):
            result_array.append(str(int(self.bin_array[i]) &
                          int(hack_number2.bin_array[i])))
        result_string = ''.join(result_array)
        result = self._bit_string_to_dec(result_string) 
        return result

    def bitor(self, hack_number2):
        result_array = []
        for i in range(0,16):
            result_array.append(str(int(self.bin_array[i]) | 
                          int(hack_number2.bin_array[i])))
        result_string = ''.join(result_array)
        result = self._bit_string_to_dec(result_string) 
        return result

    def bitnot(self):
        result_array = []
        for i in range(0,16):
            if int(self.bin_array[i]) == 1:
                result_array.append('0')
            elif int(self.bin_array[i]) == 0:
                result_array.append('1')
        result_string = ''.join(result_array)
        result = self._bit_string_to_dec(result_string) 
        return result
        

def cleanup(line):
    line = line.replace(' ','') # Deletes white space
    if '//' in line: # Deletes comments
        line = line[:line.index('//') + 1]
        line = line.replace('/','')
    return line

def find_eol(line):
    clean_line = line.replace('\n', '').replace('\r', '')
    return len(clean_line)

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

def bitwise_operate(operation):
    if operation == 'an':
        value = stack[-1].bitand(stack[-2])
    elif operation == 'or':
        value = stack[-1].bitor(stack[-2])
    elif operation == 'no':
        value = stack[-1].bitnot()
    return value 

def compare_operate(operation):
    if operation == 'eq':
        value = -1 * (stack[-2].dec_value == stack[-1].dec_value)
    elif operation == 'gt':
        value = -1 * (stack[-2].dec_value > stack[-1].dec_value)
    elif operation == 'lt':    
        value = -1 * (stack[-2].dec_value < stack[-1].dec_value)
    return value

def arithmetic_operate(operation):
    if operation == 'ad':
        value = stack[-2].dec_value + stack[-1].dec_value
    if operation == 'su':
        value = stack[-2].dec_value - stack[-1].dec_value
    if operation == 'ne':
        value = -1 * stack[-1].dec_value
    return value

def operate(operation):
    if operation in ('an', 'or', 'no'):
        value = bitwise_operate(operation)
    elif operation in ('eq', 'gt', 'lt'):
        value = compare_operate(operation)
    elif operation in ('ad', 'su', 'ne'):
        value = arithmetic_operate(operation)
    return value        

def pass_through(vm_file):
    global stack
    RAM_loc = None
    new_file_name = vm_file.replace('vm', 'asm')
    asm = open(new_file_name, 'w') # asm is new '.asm' file.
    f = open(vm_file, 'r')
    
    bi_command_list = {'ad':'+', 'su':'-', 'eq':'=', 'gt':'>',
                       'lt':'<', 'an':'&', 'or':'|'}
    un_command_list = {'ne':'-', 'no':'!'} 

    for line in f:
    
        lines_to_write = [] # Initizalize line to write to new .asm file.
        line = cleanup(line)
        if line == '':
            continue
        eol = find_eol(line)
        segment_type = get_segment_type(line)

        if segment_type is not 'operation':
            RAM_loc = segments[segment_type]
            val_index = re.search('\d', line)
            val = int(line[val_index.start():eol+1])
            if segment_type == 'temp': 
                RAM_loc = 5 + val
            if segment_type == 'pointer':
                RAM_loc = 3 + val
            if 'pop' in line:
                transfer = stack.pop()
                eval(segment_type)[val] = transfer
                if segment_type != ('temp' or 'pointer'):
                    lines_to_write = ['@%d' % val,
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
                else:
                    lines_to_write = ['@SP',
                                      'M=M-1',
                                      'A=M',
                                      'D=M',
                                      '@%s' % RAM_loc,
                                      'M=D']


            if 'push' in line:
                if segment_type == 'constant':
                    stack.append(HackNumber(val)) # constants
                    lines_to_write = ['@%d' % stack[-1].dec_value, # constants
                                      'D=A',
                                      '@SP',
                                      'A=M',
                                      'M=D',
                                      '@SP',
                                      'M=M+1']
                else:
                    transfer = eval(segment_type)[val]
                    stack.append(transfer)
                    if segment_type != ('temp' or 'pointer'):
                        lines_to_write = ['@%d' % val,
                                          'D=A',
                                          '@%s' % RAM_loc,
                                          'D=D+A',
                                          'A=D', # Where we want to get value
                                          'D=M', # D is now number to push
                                          '@SP',
                                          'M=M-1',
                                          'A=M',
                                          'M=D']
                    else:
                        lines_to_write = ['@%s' % RAM_loc,
                                          'D=M',
                                          '@SP',
                                          'M=M-1',
                                          'A=M',
                                          'M=D']

        else:
            operation = line[0:2]

            if operation in bi_command_list:
                lines_to_write = ['@SP',
                                  'M=M-1',
                                  'M=M-1',
                                  'A=M',
                                  'D=M',
                                  '@SP',
                                  'M=M+1',
                                  'A=M']
                value = operate(operation)
                if operation in ('eq', 'gt', 'lt'):
                    lines_to_write.append('D=%d' % value)
                else:
                    lines_to_write.append('D=D%sM'
                                          % bi_command_list[operation])
                lines_to_write.extend(('@SP',
                                       'M=M-1',
                                       'A=M',
                                       'M=D',
                                       '@SP',
                                       'M=M+1'))
                stack.pop()
                stack.pop()
                stack.append(HackNumber(value))

            if operation in un_command_list:
                lines_to_write = ['@SP',
                                  'M=M-1',
                                  'A=M',
                                  'M=%sM' % un_command_list[operation],
                                  '@SP',
                                  'M=M+1']
                value = operate(operation)
                stack.pop()
                stack.append(HackNumber(value))
    
        write_to_asm(lines_to_write, asm)
    f.close()
    asm.close()

#MAIN
stack = []
local = {}
argument = {}
this = {}
that = {}
static = {}
temp = [0,0,0,0,0,0,0]
pointer = [0,0,0]

segments = {'argument': 'ARG', 'local': 'LCL', 'this': 'THIS', 'that': 'THAT',
            'constant': 'SP', 'temp': 5} 

if __name__ == '__main__':
    script, vm_file = argv

    pass_through(vm_file)

