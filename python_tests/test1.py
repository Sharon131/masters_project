from itertools import accumulate
from collections import Counter

text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
text_eng = "On the other hand, we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment, so blinded by desire, that they cannot foresee the pain and trouble that are bound to ensue, and equal blame belongs to those who fail in their duty through weakness of will, which is the same as saying through shrinking from toil and pain. These cases are perfectly simple and easy to distinguish. In a free hour, when our power of choice is untrammelled and when nothing prevents our being able to do what we like best, every pleasure is to be welcomed and every pain avoided."
fixed_freqs_1024 = {' ': 171, 'e': 88, 't': 64, 'a': 62, 'n': 56, 'i': 56, 'o': 55, 's': 53, 'r': 52, 'l': 32, 'd': 32, 'h': 26, 'c': 25, 'u': 19,
                    'm': 18, 'p': 17, 'f': 15, 'g': 12, '.': 11, 'b': 10, ',': 8, 'v': 7, 'x': 2, 'q': 1, 'L': 1, 'U': 1, 'D': 1, 'E': 1,
                    'O': 1, 'w': 1, 'k': 1, 'z': 1, 'y': 1, 'T': 1, 'I': 1}
fixed_freqs_512 = {' ': 85, 'e': 44, 't': 32, 'a': 31, 'n': 28, 'i': 28, 'o': 27, 's': 26, 'r': 26, 'l': 16, 'd': 16, 'h': 13, 'c': 12, 'u': 9,
                    'm': 9, 'p': 8, 'f': 7, 'g': 6, '.': 5, 'b': 5, ',': 4, 'v': 3, 'x': 1, 'q': 1, 'L': 1, 'U': 1, 'D': 1, 'E': 1,
                   'O': 1, 'w': 1, 'k': 1, 'z': 1, 'y': 1, 'T': 1, 'I': 1}

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
    state = l*M
    shift_factor = (2**k)
    range_factor = l * shift_factor
    bitstream_prev_len = 0

    for s in s_input:  # iterate over the input
        # Output bits to the stream to bring the state in the range for the next encoding

        while state >= range_factor * freqs[s]:
            bitstream.append(state % shift_factor)
            state = state // shift_factor
            # print("while:", state)
        # print("Before step state: ", state)
        state = rans_step(s, state, freqs)  # The rANS encoding step
        # print("After step, state: ", state, "bitstream len: ", len(bitstream) - bitstream_prev_len)
        bitstream_prev_len = len(bitstream)
    return state, bitstream


def prepare_text_for_ans(input_text: str):
    counter = Counter(input_text)

    return counter


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

    dec_text = ""
    while len(bitstream) > 0:
        symbol, state = drans_step(state, freqs)

        dec_text = symbol + dec_text
        while state < range_factor * M:
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
    print("state, bitstream:", state, bitstream)
    print("bitstream length: ", len(bitstream))
    decoded_text = decode_stream_ans(state, bitstream, freqs, k, l)
    print("decoded text: ", decoded_text)
    print("decoding successfull: ", decoded_text == text)


if __name__ == '__main__':
    print('PyCharm')

    freqs = prepare_text_for_ans(text)
    cum = count_cummulative(freqs)
    print(freqs)
    print(cum)
    print(sum(freqs.values()))
    print(len(freqs))
    print(len(cum.keys()))

    first_step = rans_step('L', 445, freqs)
    print(first_step)
    print(drans_step(first_step, freqs))

    print("Reversed cummulative symbol", cummulative_inverse(cum, 15))

    check_encoding_decoding(text, freqs, 1, 1)

    check_encoding_decoding(text, freqs, 1, 4)
    check_encoding_decoding(text, freqs, 1, 8)

    check_encoding_decoding(text, freqs, 2, 1)
    check_encoding_decoding(text, freqs, 4, 1)
    check_encoding_decoding(text, freqs, 8, 1)
    check_encoding_decoding(text, freqs, 10, 1)
    # print("k=1, l=10")
    # (state, bitstream) = stream_ans(text, freqs, 1, 10)
    # print(state, bitstream)
    # print(len(bitstream))
    # decoded_text = decode_stream_ans(state, bitstream, freqs, 1, 10)
    # print("decoding", decoded_text)
    # print("decoding successfull: ", decoded_text == text)

    print("------No division------")
    (state, bitstream) = stream_ans_no_div(text, freqs)
    print(state, bitstream)
    print(len(bitstream))

    decoded_text = decode_stream_ans_no_div(state, bitstream, freqs)
    print("decoding", decoded_text)
    print("decoding successfull: ", decoded_text == text)
