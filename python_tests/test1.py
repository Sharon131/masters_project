from itertools import accumulate
from collections import Counter
from math import log2, ceil
import time

# image_peppers_bmp = open("test_images/peppers.bmp", "br")
# peppers_bmp = image_peppers_bmp.read()
# image_peppers_bmp.close()

size_of_text = 32
# generated_text_file = open("generated_" + str(size_of_text) + ".txt", "r")
# generated_text = generated_text_file.read()
# generated_text_file.close()


def prepare_large_text_for_ans(filename, size, size_of_chunk=2**16):
    generated_text_file = open(filename, "r")
    counter = Counter()
    for i in range(size // size_of_chunk):
        input_text = generated_text_file.read(size_of_chunk)
        counter.update(input_text)
    generated_text_file.close()

    return counter


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


def stream_ans(s_input: str, freqs: Counter, k: int, l: int, state=0):
    M = sum(freqs.values())
    # M = 1024
    bitstream = []
    shift_factor = (2**k)
    range_factor = l * shift_factor
    if state == 0:
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


def analise_encoding_k(to_encode, freqs, filename="", path=""):
    # write to csv file number of bits needed to encode depending on l and k
    if filename == "":
        filename = "test_k_" + str(size_of_text) + ".csv"
    M = sum(freqs.values())
    with open(path + "/" + filename, "w") as csv_file:
        csv_file.write("M;l;k;sum\n")
        l = 1
        for j in range(0, 8):
            k = 1
            for i in range(0, 8):
                (state, bitstream) = stream_ans(to_encode, freqs, k, l)
                bitstream_len = len(bitstream) * k
                state_width = ceil(log2(M * l * (2 ** k)))
                csv_file.write('{};{};{};{}\n'.format(M, l, k, state_width + bitstream_len))
                k *= 2
            l *= 2
            print("File ", filename, "finished for l=", l)
        csv_file.close()


def analise_encoding_l(to_encode, freqs, filename="", path=""):
    # write to csv file number of bits needed to encode depending on l and k
    if filename == "":
        filename = "test_l_" + str(size_of_text) + ".csv"
    M = sum(freqs.values())
    with open(path + "/" + filename, "w") as csv_file:
        csv_file.write("M;l;k;sum\n")
        k = 1
        for j in range(0, 8):
            l = 1
            for i in range(0, 8):
                (state, bitstream) = stream_ans(to_encode, freqs, k, l)
                bitstream_len = len(bitstream) * k
                state_width = ceil(log2(M * l * (2 ** k)))
                csv_file.write(
                    '{};{};{};{}\n'.format(M, l, k, state_width + bitstream_len))
                l *= 2
            k *= 2
            print("File ", filename, "finished for k=", k)
        csv_file.close()


def analise_encoding_large_file_l(filename_to_encode, freqs, size=2**32, size_of_chunk=2**16, filename="", path=""):
    # write to csv file number of bits needed to encode depending on l and k
    if filename == "":
        filename = "test_l_" + str(size_of_text) + ".csv"
    M = sum(freqs.values())
    with open(path + "/" + filename, "w") as csv_file:
        csv_file.write("M;l;k;sum\n")
        k = 1
        for j in range(0, 8):
            l = 1
            for i in range(0, 8):
                state = M * l
                bitstream = []
                with open(filename_to_encode, "r") as file_to_encode:
                    for i in range(size // size_of_chunk):
                        to_encode = file_to_encode.read(size_of_chunk)
                        (state, bitstream_new) = stream_ans(to_encode, freqs, k, l, state=state)
                        bitstream.extend(bitstream_new)
                        print("Chunk: ", i, size // size_of_chunk)
                    file_to_encode.close()
                bitstream_len = len(bitstream) * k
                state_width = ceil(log2(M * l * (2 ** k)))
                csv_file.write(
                    '{};{};{};{}\n'.format(M, l, k, state_width + bitstream_len))
                l *= 2
            k *= 2
            print("k=", k)
        csv_file.close()

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

    # to_encode = generated_text
    # print(len(generated_text))
    # freqs = prepare_text_for_ans(to_encode)
    freqs = prepare_large_text_for_ans("generated_32.txt", 2**32)

    entropy_per_symbol = calculate_entropy(freqs)
    print("entropy: ", entropy_per_symbol)
    print("entropy all: ", entropy_per_symbol * sum(freqs.values()))
    # write_distribution(freqs, "lorem_distribution.csv")

    path_to_results = "generated_results"
    print("-----Analise for k-----")
    # analise_encoding_k(to_encode, freqs, path=path_to_results)

    # analise_encoding_k(to_encode, freqs, 1, path=path_to_results)
    # analise_encoding_k(to_encode, freqs, 2, path=path_to_results)
    # analise_encoding_k(to_encode, freqs, 4, path=path_to_results)
    # analise_encoding_k(to_encode, freqs, 8, path=path_to_results)
    # analise_encoding_k(to_encode, freqs, 16, path=path_to_results)
    # analise_encoding_k(to_encode, freqs, 32, path=path_to_results)
    # analise_encoding_k(to_encode, freqs, 64, path=path_to_results)
    # analise_encoding_k(to_encode, freqs, 128, path=path_to_results)

    print("-----Analise for l-----")

    # analise_encoding_l(to_encode, freqs, path=path_to_results)

    analise_encoding_large_file_l("generated_32.txt", freqs, path=path_to_results)
    # analise_encoding_l(to_encode, freqs, 1, path=path_to_results)
    # analise_encoding_l(to_encode, freqs, 2, path=path_to_results)
    # analise_encoding_l(to_encode, freqs, 4, path=path_to_results)
    # analise_encoding_l(to_encode, freqs, 8, path=path_to_results)
    # analise_encoding_l(to_encode, freqs, 16, path=path_to_results)
    # analise_encoding_l(to_encode, freqs, 32, path=path_to_results)
    # analise_encoding_l(to_encode, freqs, 64, path=path_to_results)
    # analise_encoding_l(to_encode, freqs, 128, path=path_to_results)

    # print("------No division------")
    # (state, bitstream) = stream_ans_no_div(to_encode, freqs)
    # print(state, bitstream)
    # print(len(bitstream))
    #
    # decoded_text = decode_stream_ans_no_div(state, bitstream, freqs)
    # print("decoding", decoded_text)
    # print("decoding successfull: ", decoded_text == to_encode)
