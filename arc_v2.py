import bitfile


def mask_bit(x):
    return (1 << (PRECISION - (1 + x)))

def get_lower(c):
    if type(c) == str:      # handle strings
        return ord(c)
    return c

def get_upper(c):
    if type(c) == str:      # handle strings
        return ord(c) + 1
    return c + 1

EOF_CHAR = 256

# number of bits used to compute running code values
PRECISION = 16

# mask to clear the msb of probability values
MSB_MASK = ((1 << (PRECISION - 1)) - 1)

# 2 bits less than precision. keeps lower and upper bounds from crossing
MAX_PROBABILITY = (1 << (PRECISION - 2))

lower = 0  # lower bound of current code range
upper = 0xFFFF  # upper bound of current code range

code = 0  # current MSBs of encode input stream

underflow_bits = 0  # current underflow bit count

# The probability lower and upper ranges for each symbol
ranges = [0 for i in xrange(get_upper(EOF_CHAR) + 1)]
cumulative_prob = 0  # cumulative probability  of all ranges

infile = None
outfile = None

def encode_file(input_file_name, output_file_name):

    global infile
    global outfile

    # read through input file and compute ranges
    infile = open(input_file_name, 'rb')
    build_probability_range_list()
    infile.seek(0)

    # write header with ranges to output file
    outfile = bitfile.BitFile()
    outfile.open(output_file_name, 'wb')
    write_header()

    # encode file 1 byte at at time
    c = infile.read(1)
    while (c != ''):
        apply_symbol_range(c)
        write_encoded_bits()
        c = infile.read(1)

    infile.close()
    apply_symbol_range(EOF_CHAR)   # encode an EOF
    write_encoded_bits()

    write_remaining()              # write out least significant bits
    outfile.close()

def build_probability_range_list():

    global cumulative_prob
    global ranges

    # start with no symbols counted
    count_array = [0 for i in xrange(EOF_CHAR)]

    c = infile.read(1)
    while (c != ''):
        count_array[ord(c)] += 1
        c = infile.read(1)

    total_count = sum(count_array)

    # rescale counts to be < MAX_PROBABILITY
    if total_count >= MAX_PROBABILITY:
        rescale_value = (total_count / MAX_PROBABILITY) + 1

        for index, value in enumerate(count_array):
            if value > rescale_value:
                count_array[index] = value / rescale_value
            elif value != 0:
                count_array[index] = 1

    # copy scaled symbol counts to range list upper range (add EOF)
    ranges = [0] + count_array + [1]
    cumulative_prob = sum(count_array)

    # convert counts to a range of probabilities
    symbol_count_to_probability_ranges()

def symbol_count_to_probability_ranges():

    global cumulative_prob
    global ranges

    ranges[0] = 0                     # absolute lower bound is 0
    ranges[get_upper(EOF_CHAR)] = 1  # add one EOF character
    cumulative_prob += 1

    for c in xrange(EOF_CHAR + 1):
        ranges[c + 1] += ranges[c]

def write_header():
    previous = 0

    for c in xrange(EOF_CHAR):
        if ranges[get_upper(c)] > previous:
            # some of these symbols will be encoded
            outfile.put_char(c)
            # calculate symbol count
            previous = (ranges[get_upper(c)] - previous)

            # write out PRECISION - 2 bit count
            outfile.put_bits_ltom(previous, (PRECISION - 2))

            # current upper range is previous for the next character
            previous = ranges[get_upper(c)]

    # now write end of table (zero count)
    outfile.put_char(0)
    previous = 0
    outfile.put_bits_ltom(previous, (PRECISION - 2))


def apply_symbol_range(symbol):
    global lower
    global upper

    range = upper - lower + 1           # current range

    # scale the upper range of the symbol being coded
    rescaled = ranges[get_upper(symbol)] * range
    rescaled /= cumulative_prob

    # new upper = old lower + rescaled new upper - 1
    upper = lower + rescaled - 1

    # scale lower range of the symbol being coded
    rescaled = ranges[get_lower(symbol)] * range
    rescaled /= cumulative_prob

    # new lower = old lower + rescaled new lower
    lower = lower + rescaled



def write_encoded_bits():
    global lower
    global upper
    global underflow_bits

    mask_bit_zero = mask_bit(0)
    mask_bit_one = mask_bit(1)

    while True:
        if (upper ^ ~lower) & mask_bit_zero:
            # MSBs match, write them to output file
            outfile.put_bit((upper & mask_bit_zero) != 0)

            # we can write out underflow bits too
            while underflow_bits > 0:
                outfile.put_bit((upper & mask_bit_zero) == 0)
                underflow_bits -= 1

        elif (~upper & lower) & mask_bit_one:
            underflow_bits += 1
            lower &= ~(mask_bit_zero | mask_bit_one)
            upper |= mask_bit_one
        else:
            return              # nothing left to do

        lower &= MSB_MASK
        lower <<= 1
        upper &= MSB_MASK
        upper <<= 1
        upper |= 0x0001

def write_remaining():
    global underflow_bits

    mask_bit_one = mask_bit(1)
    outfile.put_bit((lower & mask_bit_one) != 0)

    # write out any unwritten underflow bits
    underflow_bits += 1
    for i in xrange(underflow_bits):
        outfile.put_bit((lower & mask_bit_one) == 0)

def decode_file(input_file_name, output_file_name):

    global infile
    global outfile


    # open input and build probability ranges from header in file
    infile = bitfile.BitFile()
    infile.open(input_file_name, 'rb')


    read_header()  # build probability ranges from header in file

    # read start of code and initialize bounds
    initialize_decoder()

    outfile = open(output_file_name, 'wb')

    # decode one symbol at a time
    while True:
        # get the unscaled probability of the current symbol
        unscaled = get_unscaled_code()

        # figure out which symbol has the above probability
        c = get_symbol_from_probability(unscaled)
        if c == EOF_CHAR:
            # no more symbols
            break

        outfile.write(chr(c))

        # factor out symbol
        apply_symbol_range(c)
        read_encoded_bits()

    outfile.close()
    infile.close()

def read_header():
    global cumulative_prob
    global ranges

    cumulative_prob = 0
    ranges = [0 for i in xrange(get_upper(EOF_CHAR) + 1)]
    count = 0

    # read [character, probability] sets
    while True:
        c = infile.get_char()

        # read (PRECISION - 2) bit count
        count = infile.get_bits_ltom(PRECISION - 2)

        if count == 0:
            # 0 count means end of header
            break


        ranges[get_upper(c)] = count
        cumulative_prob += count

    # convert counts to range list
    symbol_count_to_probability_ranges()

def initialize_decoder():
    global lower
    global upper
    global code

    code = 0

    # read PRECISION MSBs of code one bit at a time
    for i in xrange(PRECISION):
        code <<= 1

        try:
            next_bit = infile.get_bit()
        except EOFError:
            # Encoded file out of data bits, just shift bits.
            pass
        except:
            raise       # other exception.  Let calling code handle it.
        else:
            code |= next_bit

    # start with full probability range [0%, 100%)
    lower = 0
    upper = 0xFFFF        # all ones

def get_unscaled_code():
    range = upper - lower + 1

    # reverse the scaling operations from apply_symbol_range
    unscaled = code - lower + 1
    unscaled = unscaled * cumulative_prob - 1
    unscaled /= range
    return unscaled

def get_symbol_from_probability(probability):
    # initialize indices for binary search
    first = 0
    last = get_upper(EOF_CHAR)
    middle = last / 2

    # binary search
    while (last >= first):
        if probability < ranges[get_lower(middle)]:
            # lower bound is higher than probability
            last = middle - 1
            middle = first + ((last - first) / 2)
        elif probability >= ranges[get_upper(middle)]:
            # upper bound is lower than probability
            first = middle + 1
            middle = first + ((last - first) / 2)
        else:
            # we must have found the right value
            return middle

    # error: none of the ranges include the probability
    raise ValueError('Probability not in range.')

def read_encoded_bits():

    global lower
    global upper
    global code

    mask_bit_zero = mask_bit(0)
    mask_bit_one = mask_bit(1)

    while True:

        if (upper ^ ~lower) & mask_bit_zero:
            # MSBs match, allow them to be shifted out
            pass
        elif (~upper & lower) & mask_bit_one:
            lower &= ~(mask_bit_zero | mask_bit_one)
            upper |= mask_bit_one
            code ^= mask_bit_one
        else:
            # nothing to shift out
            return

        lower &= MSB_MASK
        lower <<= 1
        upper &= MSB_MASK
        upper <<= 1
        upper |= 1
        code &= MSB_MASK
        code <<= 1

        try:
            next_bit = infile.get_bit()
        except EOFError:
            pass        # either out of bits or error occurred.
        except:
            raise       # other exception.  Let calling code handle it.
        else:
            code |= next_bit


def main():

    #encode file (input, output)
    encode_file('input.txt', 'decoded2.txt')
    # decode file (input, output)
    decode_file('decoded2.txt', 'decoded_v2.txt')

if __name__ == '__main__':
    main()