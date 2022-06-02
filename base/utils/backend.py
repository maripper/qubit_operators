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
    common_ground = []
    for q in range(n):
        if S[q] == R[q]:
            # If both used the same basis, add
            # this to the list of 'good' bits
            common_ground.append(data[q])
    return common_ground

def safety_check(bits, choice):
    sample = []
    for i in choice:
        # use np.mod to make sure the
        # bit we sample is always in 
        # the list range
        i = np.mod(i, len(bits))
        # pop(i) removes the element of the
        # list at index 'i'
        sample.append(bits.pop(i))
    return sample

def sender_key(sender_base, receiver_base, sender_bits):
    sender_key = common_ground(sender_base, receiver_base, sender_bits)
    
    return sender_key
def receiver_key(sender_base, receiver_base, receiver_results):
    receiver_key = common_ground(sender_base, receiver_base, receiver_results)
    
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

def receiver_check(sender_base, receiver_base, receiver_results):
    key = receiver_key(sender_base, receiver_base, receiver_results)
    with open("bit_selection.txt") as file:
        bit_selection = file.readlines()
    receiver_sample = safety_check(key, bit_selection)
    
    return receiver_sample,key

def sender_check(sender_base, receiver_base, sender_results):
    key = sender_key(sender_base, receiver_base, sender_results)
    sender_sample = safety_check(key, bit_selection)
    with open("bit_selection.txt") as file:
     bit_selection = file.readlines()
    print("sender_sample = "+ str(sender_sample))
    return sender_sample,key
def compare(sender_sample,receiver_sample):
    if(sender_sample==receiver_sample):
        return True
    return False

def encode_message(bits, bases):
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

def measure_message(message, bases):
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

def sender_bits():
    np.random.seed(seed=0)
    n = 100
    ## Step 1
    # sender generates bits
    sender_bits = randint(2, size=n)
    print('bits',sender_bits)
    #encode each bit on qubit in the  X  or  Z -basis at random, and stores the choice for each qubit in sender_bases. In this case, a 0 means "prepare in the  Z -basis", and a 1 means "prepare in the  X -basis" 
    # Create an array to tell us which qubits
    # are encoded in which bases
    sender_bases = randint(2, size=n)
    print('base',sender_bases)

    message = encode_message(sender_bits, sender_bases)
    return(message,sender_bits,sender_bases,n)

def receiver_bits(n,message):
  receiver_base = randint(2, size=n)
  receiver_results = measure_message(message, receiver_base)
  print(receiver_results)
  return receiver_results,receiver_base
