from itertools import accumulate
from collections import Counter
from math import log2, ceil
import time
from randomText import RandomTextClient

text_lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
fixed_freqs_1024 = {' ': 171, 'e': 88, 't': 64, 'a': 62, 'n': 56, 'i': 56, 'o': 55, 's': 53, 'r': 52, 'l': 32, 'd': 32, 'h': 26, 'c': 25, 'u': 19,
                    'm': 18, 'p': 17, 'f': 15, 'g': 12, '.': 11, 'b': 10, ',': 8, 'v': 7, 'x': 2, 'q': 1, 'L': 1, 'U': 1, 'D': 1, 'E': 1,
                    'O': 1, 'w': 1, 'k': 1, 'z': 1, 'y': 1, 'T': 1, 'I': 1}
fixed_freqs_512 = {' ': 85, 'e': 44, 't': 32, 'a': 31, 'n': 28, 'i': 28, 'o': 27, 's': 26, 'r': 26, 'l': 16, 'd': 16, 'h': 13, 'c': 12, 'u': 9,
                    'm': 9, 'p': 8, 'f': 7, 'g': 6, '.': 5, 'b': 5, ',': 4, 'v': 3, 'x': 1, 'q': 1, 'L': 1, 'U': 1, 'D': 1, 'E': 1,
                   'O': 1, 'w': 1, 'k': 1, 'z': 1, 'y': 1, 'T': 1, 'I': 1}

# image_peppers_bmp = open("test_images/peppers.bmp", "br")
# peppers_bmp = image_peppers_bmp.read()
# image_peppers_bmp.close()

image_peppers_jpg = open("test_images/peppers.jpg", "br")
peppers_jpg = image_peppers_jpg.read()
image_peppers_jpg.close()

# image_peppers_png = open("test_images/peppers.png", "br")
# peppers_png = image_peppers_png.read()
# image_peppers_png.close()

def prepare_text_for_ans(input_text: str):
    counter = Counter(input_text)

    return counter


def count_cummulative(freqs: Counter):
    cum = dict()
    items = sorted(freqs.items(), key=lambda x: x[1])
    prev_key = items[0][0]
    cum[prev_key] = 0
    for item in items:
        key = item[0]
        if key != prev_key:
            cum[key] = cum[prev_key] + freqs[prev_key]
            prev_key = key

    return cum


def rans_step(symbol, state: int, freqs: Counter):
    M = sum(freqs.values())
    # M = 1024
    C = count_cummulative(freqs)

    return (state // freqs[symbol]) * M + C[symbol] + state % freqs[symbol]


def stream_ans(s_input: str, freqs: Counter, k: int, l: int):
    M = sum(freqs.values())
    # M = 1024
    bitstream = []
    shift_factor = (2**k)
    range_factor = l * shift_factor
    state = M * l

    for s in s_input:  # iterate over the input
        # Output bits to the stream to bring the state in the range for the next encoding
        while state >= range_factor * freqs[s]:
            bitstream.append(state % shift_factor)
            state = state // shift_factor
        state = rans_step(s, state, freqs)  # The rANS encoding step
    return state, bitstream


def cummulative_inverse(cumm_freqs: dict, slot: int):
    items = sorted(cumm_freqs.items(), key=lambda x: x[1])
    prev_key = items[0][0]
    last_key = items[-1][0]
    for key, value in items:
        if slot < value:
            return prev_key
        prev_key = key

    return last_key


def drans_step(state, freqs: Counter):
    M = sum(freqs.values())
    # M = 1024
    C = count_cummulative(freqs)
    slot = state % M
    symbol = cummulative_inverse(C, slot)
    prev_state = state // M * freqs[symbol] + slot - C[symbol]
    return symbol, prev_state


def decode_stream_ans(state, bitstream: list, freqs, k: int, l: int):
    M = sum(freqs.values())
    # M = 1024
    # cumm_freqs = count_cummulative(freqs)
    shift_factor = (2**k)
    range_factor = l

    # dec_text = ""
    dec_text = bytes()
    while len(dec_text) < M:
        symbol, state = drans_step(state, freqs)

        dec_text = symbol.to_bytes(1, "big") + dec_text
        while state < range_factor * M and len(bitstream) > 0:
            bits = bitstream.pop()
            state = state * shift_factor + bits

    return dec_text


def rans_step_no_div(symbol, state: int, freqs: Counter):
    M = sum(freqs.values())
    # M = 1024
    C = count_cummulative(freqs)

    return M + C[symbol] + state - freqs[symbol]


def stream_ans_no_div(s_input: str, freqs: Counter):
    M = sum(freqs.values())
    # M = 1024
    bitstream = []
    state = M
    range_factor = 2

    for s in s_input:  # iterate over the input
        # Output bits to the stream to bring the state in the range for the next encoding
        while state >= range_factor * freqs[s]:
            bitstream.append(state % 2)
            state = state // 2
        state = rans_step_no_div(s, state, freqs)  # The rANS encoding step
    return state, bitstream


def drans_step_no_div(state, freqs: Counter):
    M = sum(freqs.values())
    # M = 1024
    C = count_cummulative(freqs)
    slot = state - M
    symbol = cummulative_inverse(C, slot)
    prev_state = freqs[symbol] + slot - C[symbol]
    return symbol, prev_state


def decode_stream_ans_no_div(state, bitstream: list, freqs):
    M = sum(freqs.values())
    # M = 1024
    # cumm_freqs = count_cummulative(freqs)

    dec_text = ""
    while len(bitstream) > 0:
        symbol, state = drans_step_no_div(state, freqs)

        dec_text = symbol + dec_text
        while state < M:
            bits = bitstream.pop()
            state = state * 2 + bits

    return dec_text


def check_encoding_decoding(text, freqs, l, k):
    print("------------")
    print("l=", l, "k=", k)
    (state, bitstream) = stream_ans(text, freqs, k, l)
    # print("state, bitstream:", state, bitstream)
    print("bitstream length: ", len(bitstream))
    start = time.time()
    decoded_text = decode_stream_ans(state, bitstream, freqs, k, l)
    end = time.time()
    # print("decoded text: ", decoded_text)
    print("decoding successfull: ", decoded_text == text)
    print("decoding time for l=", l, "k=", k, ":", end - start)


def analise_encoding_k(to_encode, freqs, l, filename=""):
    # write to csv file number of bits needed to encode depending on l and k
    if filename == "":
        filename = "test_k_l_" + l + ".csv"
    M = sum(freqs.values())
    with open("peppers_png_analise/" + filename, "w") as csv_file:
        csv_file.write("M;l;k;bitstream_len;sum\n")
        k = 1
        for i in range(1, 8):
            (state, bitstream) = stream_ans(to_encode, freqs, k, l)
            bitstream_len = len(bitstream) * k
            # decoded = decode_stream_ans(state, bitstream, freqs, k, l)
            # if decoded == to_encode:
            state_width = ceil(log2(M * l * (2 ** k)))
            csv_file.write('{};{};{};{};{}\n'.format(M, l, k, bitstream_len, state_width + bitstream_len))
            # else:
            #     print("Encoding went wrong for k=", k, " and l=", l)
            #     print(decoded)
            k *= 2
        csv_file.close()
        print("File ", filename, "finished for l=", l)


def analise_encoding_l(to_encode, freqs, k, filename=""):
    # write to csv file number of bits needed to encode depending on l and k
    if filename == "":
        filename = "test_l_k_" + k + ".csv"
    M = sum(freqs.values())
    with open("peppers_png_analise/" + filename, "w") as csv_file:
        csv_file.write("M;l;k;bitstream_len;sum\n")
        l = 1
        for i in range(1, 8):
            (state, bitstream) = stream_ans(to_encode, freqs, k, l)
            bitstream_len = len(bitstream) * k
            decoded = decode_stream_ans(state, bitstream, freqs, k, l)
            if decoded == to_encode:
                state_width = ceil(log2(M * l * (2 ** k)))
                csv_file.write(
                    '{};{};{};{};{}\n'.format(M, l, k, bitstream_len, state_width + bitstream_len))
            else:
                print("Encoding went wrong for k=", k, " and l=", l)
                print(decoded)
            l *= 2
        csv_file.close()
        print("File ", filename, "finished for k=", k)


def write_distribution(freqs, filename="distribution_new.csv"):
    with open(filename, "w") as write_file:
        write_file.write("no;freq\n")
        M = sum(freqs.values())
        for i in range(0, 256):
            write_file.write("{};{}\n".format(i, freqs[chr(i)]/M*100))
        write_file.close()


def calculate_entropy(freqs: Counter):
    M = sum(freqs.values())
    entropy = 0
    items = freqs.items()
    for item in items:
        entropy += - item[1] / M * log2(item[1] / M)

    return entropy


if __name__ == '__main__':
    print('PyCharm')

    to_encode = peppers_jpg
    freqs = prepare_text_for_ans(to_encode)

    print("entropy: ", calculate_entropy(freqs))
    # write_distribution(freqs, "lorem_distribution.csv")

    print("-----Analise for k-----")
    analise_encoding_k(to_encode, freqs, 1, "test_k_l_1.csv")
    analise_encoding_k(to_encode, freqs, 2, "test_k_l_2.csv")
    analise_encoding_k(to_encode, freqs, 4, "test_k_l_4.csv")
    analise_encoding_k(to_encode, freqs, 8, "test_k_l_8.csv")
    analise_encoding_k(to_encode, freqs, 9, "test_k_l_9.csv")
    analise_encoding_k(to_encode, freqs, 10, "test_k_l_10.csv")

    print("-----Analise for l-----")

    analise_encoding_l(to_encode, freqs, 1, "test_l_k_1.csv")
    analise_encoding_l(to_encode, freqs, 2, "test_l_k_2.csv")
    analise_encoding_l(to_encode, freqs, 4, "test_l_k_4.csv")
    analise_encoding_l(to_encode, freqs, 8, "test_l_k_8.csv")
    analise_encoding_l(to_encode, freqs, 16, "test_l_k_16.csv")
    analise_encoding_l(to_encode, freqs, 32, "test_l_k_32.csv")
    analise_encoding_l(to_encode, freqs, 64, "test_l_k_64.csv")
    analise_encoding_l(to_encode, freqs, 128, "test_l_k_128.csv")

    # print("------No division------")
    # (state, bitstream) = stream_ans_no_div(to_encode, freqs)
    # print(state, bitstream)
    # print(len(bitstream))
    #
    # decoded_text = decode_stream_ans_no_div(state, bitstream, freqs)
    # print("decoding", decoded_text)
    # print("decoding successfull: ", decoded_text == to_encode)
