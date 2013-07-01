from sys import argv
 

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

def negate(number):
    neg_number = -1 * number
    bin_neg_number_uf = bin(neg_number)
    if bin_neg_number_uf < 0:
        cutoff = 3
    else:
        cutoff = 2
    bin_neg_number = bin_neg_number_uf[cutoff:]
    negated_array = binary_negate(bin_neg_number)
    return negated_array

def bin16_to_dec(bin_number):
    formatted_bin = "0b" + str(bin_number)
    dec_number = eval(formatted_bin)
    if dec_number > 32767:
        dec_number = dec_number-65536
    return dec_number


def binary_negate(bin_number):
    negated_array = [] 
    bin_array = bitarray(bin_number)
    sig1_index = (''.join(bin_array)).rfind('1')
    for digit in bin_array[:sig1_index]:
        if digit == '0':
            negated_array.append('1')
        elif digit == '1':
            negated_array.append('0')
    for digit in bin_array[sig1_index:]:
        negated_array.append(digit)
    return negated_array


def bitarray(number_to_convert):
    bit_array = []
    number_string = str(number_to_convert)
    for digit in number_string:
        bit_array.append(digit)
    return bit_array
        

def convert_16bit_bin(number):
    if number < 0: # Returns 16-bit 2's complement
        complemented_number = negate(number)
        return complemented_number[len(complemented_number)-16:]
    else:
        bin_number_uf = bin(number)
        bin_number = bin_number_uf[2:]
        bin_array = bitarray(bin_number)
        return bin_array

def invert_16bit_bin(number_to_invert):
    inverted_array = []
    bin_array = convert_16bit_bin(number_to_invert)
    if len(bin_array) < 16:
        extra_0s = 16 - len(bin_array)
    for each in range(0, extra_0s):
        inverted_array.append('1')
    for digit in bin_array:
        if digit == '0':
            inverted_array.append('1')
        elif digit == '1':
            inverted_array.append('0')
    number_string = ''.join(inverted_array)
    if eval(number_string) < 0:
        number_string = ''.join(negate(eval(number_string)))
    dec_number = bin16_to_dec(eval(number_string))
    return dec_number
    

def pass_through(vm_file):
    global stack
    new_file_name = vm_file.replace('vm', 'asm')
    asm = open(new_file_name, 'w') # asm is new '.asm' file.
    f = open(vm_file, 'r')
    
    bi_command_list = {'ad':'+', 'su':'-', 'eq':'=', 'gt':'>',
                       'lt':'<', 'an':'&', 'or':'|'}
    un_command_list = {'ne':'-', 'no':'!'} 

    def get_line_type(line):
        return 'arithmetic' # TODO: create entire function returning type

        

    def bi_operate(operation):
        if operation in ('eq'): 
            operand = 2 * bi_command_list[operation]
        else:
            operand = bi_command_list[operation]
        if operation in ('gt', 'lt', 'eq'): # Comparative operations
            value = -1 * eval("stack[len(stack) - 2] %s stack[len(stack) - 1]" 
                              % operand) # Python True = 1, VM True = -1.
        else: # Calculative operations
            value = eval("stack[len(stack) - 1] %s stack[len(stack) - 2]"
                         % operand) 
        return value

    def un_operate(operation):
        operand = un_command_list[operation]
        if operand == '!':
            return invert_16bit_bin(stack[len(stack) - 1]) 
        elif operand == '-':
            bin_array = convert_16bit_bin(-1 * (stack[len(stack) - 1]))
            return eval(''.join(bin_array))

    for line in f:
    
        lines_to_write = [] # Initizalize line to write to new .asm file.
        line = cleanup(line)
        if line == '':
            continue
        eol = find_eol(line)

        line_type = get_line_type(line)

        if line_type == 'arithmetic':
            
            if line[0:4] == 'push':
                stack.append(int(line[12:eol+1]))
                lines_to_write = ['@%d' % stack[len(stack) - 1],
                                  'D=A',
                                  '@SP',
                                  'A=M',
                                  'M=D',
                                  '@SP',
                                  'M=M+1']

            else:
                operation = line[0:2]

                if operation in bi_command_list:
                    lines_to_write = ['@SP',
                                      'M=M-1',
                                      'A=M',
                                      'D=M',
                                      '@SP',
                                      'M=M-1',
                                      'A=M']
                    value = bi_operate(operation)
                    if operation in ('eq', 'gt', 'lt'):
                        lines_to_write.append('M=%d' % value)
                    else:
                        lines_to_write.append('M=D%sM'
                                              % bi_command_list[operation])
                    lines_to_write.extend(('@SP', 'M=M+1'))
                    stack.pop()
                    stack.pop()
                    stack.append(value)

                if operation in un_command_list:
                    lines_to_write = ['@SP',
                                      'M=M-1',
                                      'A=M',
                                      'M=%sM' % un_command_list[operation],
                                      '@SP',
                                      'M=M+1']
                    value = un_operate(operation)
                    print value
                    stack.pop()
                    stack.append(value)
        
        write_to_asm(lines_to_write, asm)
    f.close()
    asm.close()

if __name__ == '__main__':
    script, vm_file = argv

    stack = []
    pass_through(vm_file)

