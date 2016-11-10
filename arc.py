'''
 - Author:  Group A
 - Course:  CSE 4081, Fall 2016
 - Project: Group Project, Arithmetic Coding

 How this project is meant to be run - cmd line input
 ArithmeticCoding.py < input.txt
 Outputs two text files, one with the encoding and one after the decoding
'''

import sys, os
from mpmath import *


ENCODED_FILE_NAME = "encoded.txt"
DECODED_FILE_NAME = "decoded.txt"

model = dict()
count = 0;

def buildModel(stringToEncode):
    charList = dict()
    start = mpf(0)
    global count
    for c in stringToEncode:
        count += 1
        if c in charList.keys():
            charList[c] += 1
        else:
            charList[c] = 1

    #dps has to be longer in order to correctly encode and decode loger messages
    #not sure how to calculate correct lenght

    mp.dps = count+1
    model.fromkeys(charList)
    for c, v in charList.items():
        width = mpf(charList[c]/count)
        model[c] = (start, width)
        start += charList[c]/count


def encode(stringToEncode):
    buildModel(stringToEncode)
    encodedFile = open(ENCODED_FILE_NAME, 'w')
    mp.dps = count * count
    high = mpf(1.0)
    low = mpf(0.0)
    global ultimateRange
    for c in stringToEncode:
        c_start, c_width = model[c]
        c_end = c_start + c_width
        d_range = mpf(high - low)
        ultimateRange = mpf(d_range)
        high = low + (c_end * d_range)
        low = low + (c_start * d_range)

    encodedFile.write(str(low + (high-low)/2))
    return low + (high-low)/2

def decode(encodedNumber):

    decodedFile = open(DECODED_FILE_NAME, 'w')
    mp.dps = count * count
    string = []
    high = mpf(1.0)
    low = mpf(0.0)
    d_range = mpf(high - low)
    while (d_range > ultimateRange):
        for c, (c_low, c_width) in model.items():
            c_high = mpf(c_low + c_width)
            d_range = mpf(high - low)
            if c_low <= (encodedNumber - low)/d_range < c_high:
                high = low + (d_range * c_high)
                low = low + (d_range * c_low)
                string.append(c)
                decodedFile.write(c)
                break
    return ''.join(string)


def main():
    
    stringToEncode = input()
    encodedNumber = encode(stringToEncode)
    decodedString = decode(encodedNumber)
    width =0;
    print("Message length: ", count)
    print("Arbitrary precision: ", mp.dps)
    print("Encoded message ", encodedNumber)
    print("Decoded message ", decodedString)
    print("Probability table:")
    for c, (low, high) in model.items():
        print(c, " start: ", low, " width: ", high)
        width += high
    print("width sum: ", width)
if __name__ == '__main__':
    main()
