from collections import Counter
import numpy

size_of_chunk = 2**16
number_of_bits = 32      # number of bits of size (M)
size = 2**number_of_bits
filename = "generated_" + str(number_of_bits) + ".txt"

if __name__ == '__main__':
    print('PyCharm')

    with open("alice_in_wonderland.txt", "r") as alice:
        alice_txt = alice.read()
        alice.close()

        freqs = Counter(alice_txt)
        alice_len = len(alice_txt)
        distribution = []
        for i in range(256):
            distribution.append(freqs[chr(i)]/alice_len)
        for i in range(256):
            print(i, ": ", distribution[i])

        with open(filename, "a") as new_file:
            for i in range(size // size_of_chunk):
                random_nums = numpy.random.choice(numpy.arange(0, 256), p=distribution, size=size_of_chunk)
                random_text = ''
                for letter in random_nums:
                    random_text += chr(letter)
                # print(str(random_text))
                new_file.write(random_text)
                print(str(i) + "/" + str(size // size_of_chunk))
            new_file.close()
