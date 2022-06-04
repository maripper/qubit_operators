from django.shortcuts import render

from qiskit.visualization import plot_bloch_multivector, plot_histogram

import requests as req

from django.http import JsonResponse

from qiskit import QuantumCircuit, assemble, Aer

# Do the necessary imports

import numpy as np

from qiskit import QuantumCircuit, Aer, transpile, assemble

from qiskit.visualization import plot_histogram, plot_bloch_multivector

from numpy.random import randint

import numpy as np

 

def common_ground(S, R, data,n):

    common = []

    for q in range(n):

        if S[q] == R[q]:

            # If both used the same basis, add

            # this to the list of 'good' bits

            common.append(data[q])

    return common

 

def safety_check(bits, choice):

    sample = []
    print(type(choice),choice)
    print(choice[0])
    i=0
    for i in range(len(choice)):

        # use np.mod to make sure the

        # bit we sample is always in

        # the list range
        print(i,choice[i])
        print('x',i, type(i),type(bits),bits)
        if('\n' not in str(choice[i])):
            print('enter')
            i = np.mod(int(choice[i]), len(bits))
            sample.append(bits.pop(i))
        # pop(i) removes the element of the

        # list at index 'i'

    return sample

 

def sender_key(sender_base, receiver_base, sender_bits,n):

    sender_key = common_ground(sender_base, receiver_base, sender_bits,n)

   

    return sender_key

 

def receiver_key(sender_base, receiver_base, receiver_results,n):

    receiver_key = common_ground(sender_base, receiver_base, receiver_results,n)

   

    return receiver_key

 

def public_common(n):

   

    sample_size = 15

    bit_selection = randint(n, size=sample_size)

    file = open("bit_selection.txt", "a+")

    file.seek(0)

    content = file.read()

    content = bit_selection

    file.write(content)

    file.close()

    return bit_selection

 

def receiver_check(sender_base, receiver_base, receiver_results,n):

    key = receiver_key(sender_base, receiver_base, receiver_results,n)

    with open("bit_selection.txt") as file:

        bit_selection = file.readlines()

    receiver_sample = safety_check(key, bit_selection)

   

    return receiver_sample,key

 

def sender_check(sender_base, receiver_base, sender_results,n):

    key = sender_key(sender_base, receiver_base, sender_results,n)

   

    with open("bit_selection.txt") as file:

     bit_selection = file.readlines()

   

    sender_sample = safety_check(key, bit_selection)

    print("sender_sample = "+ str(sender_sample))

    return sender_sample,key

def compare(sender_sample,receiver_sample):

    if(sender_sample==receiver_sample):

        return True

    return False

 

def encode_message(bits, bases,n):

    message = []

    for i in range(n):

        qc = QuantumCircuit(1,1)

        if bases[i] == 0: # Prepare qubit in Z-basis

            if bits[i] == 0:

                pass

            else:

                qc.x(0)

        else: # Prepare qubit in X-basis

            if bits[i] == 0:

                qc.h(0)

            else:

                qc.x(0)

                qc.h(0)

        qc.barrier()

        message.append(qc)

    return message

 

def measure_message(message, bases,n):

    backend = Aer.get_backend('aer_simulator')

    measurements = []

    for q in range(n):

        if bases[q] == 0: # measuring in Z-basis

            message[q].measure(0,0)

        if bases[q] == 1: # measuring in X-basis

            message[q].h(0)

            message[q].measure(0,0)

        aer_sim = Aer.get_backend('aer_simulator')

        qobj = assemble(message[q], shots=1, memory=True)

        result = aer_sim.run(qobj).result()

        measured_bit = int(result.get_memory()[0])

        measurements.append(measured_bit)

    return measurements

 

def sender_bits(n):

    np.random.seed(seed=3)
    ## Step 1
    sender_bit = randint(2, size=n)
    ## Step 2
    sender_bases = randint(2, size=n)
    message = encode_message(sender_bit, sender_bases,n)

    return(message,sender_bit,sender_bases)

def eve(n,message):
    eve_bases = randint(2, size=n)
    intercepted_message = measure_message(message, eve_bases,n)
    return eve_bases,intercepted_message
def receiver_bits(n,message):
    receiver_base = randint(2, size=n)
    receiver_results = measure_message(message, receiver_base,n)

    return receiver_results,receiver_base
    
 
