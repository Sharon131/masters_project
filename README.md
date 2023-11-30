## Project for my Master's thesis

This repository contains code developed for my Master's thesis "The Hardware Codec for ANS Compression". The thesis itself can be found at ... and its Latex source code at ...

The content of this repository is divided into the following directories:
- python_tests - Python scripts used for analysis
- streaming_ans - directory containing Vivado project with implementation of ANS Codec with parameters l and k fixed to 1 and variable maximum data size to encode
- streaming_ans_ip_8 - Vivado project with implementation of ANS Codec as IP with communication with microprocessor. Contains wrapping IP with FIFO and microcontroller source code
- streaming_ans_l_k - implementation of ANS Codec with l and k as entity paramters

