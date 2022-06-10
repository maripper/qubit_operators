from django.shortcuts import render

from qiskit.visualization import plot_bloch_multivector, plot_histogram

import requests as req

from django.http import JsonResponse

import random

import json

from django.views.decorators.csrf import csrf_exempt

from numpy import gcd
from numpy.random import seed, randint
# imports for Shor
from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import QFT

measurements = []

data = []


def rsa(P, Q):
    N = P * Q # the hard number to crack!

    if N % 2 == 0:
        val = P if P % 2 == 0 else Q
        raise ValueError(f"{N} can not be divisible by 2.",
                         f"{P} and {Q} are incompatible with Shor's Algorithm.")

    L = (Q - 1) * (P - 1) # number of non-common factors (1, N)

    for E in range(2, L): # between [2, L)
        if gcd(L, E) * gcd(N, E) == 1: # coprime with both L and N
            break # E is public value

    D = 1
    while True:
        if D * E % L == 1 and D != E and D != N:
            break # D is private value
        D += 1

    return ((E, N), (D, N))

def dec(code, key):
    D, N = key
    return "".join([chr(((d**D) % N) + ord('A'))
                    for d in [int(d) for d in str(code)]])

def initialize_qubits(qc, n, m):
    qc.h(range(n)) # apply hadamard gates
    qc.x(n+m-1) # set qubit to 1
    
def a_x_mod15(a, x):
    if a not in [2,7,8,11,13]:
        raise ValueError("'a' must be 2,7,8,11 or 13")
    U = QuantumCircuit(4)        
    for iteration in range(x):
        if a in [2,13]:
            U.swap(0,1)
            U.swap(1,2)
            U.swap(2,3)
        if a in [7,8]:
            U.swap(2,3)
            U.swap(1,2)
            U.swap(0,1)
        if a == 11:
            U.swap(1,3)
            U.swap(0,2)
        if a in [7,11,13]:
            for q in range(4):
                U.x(q)
    U = U.to_gate()
    U.name = f"U({x})"
    c_U = U.control()
    return c_U

def modular_exponentiation(qc, n, m, a):
    for x in range(n):
        exponent = 2**x
        qc.append(a_x_mod15(a, exponent), 
                     [x] + list(range(n, n+m)))


def apply_iqft(qc, measurement_qubits):
    qc.append(QFT(len(measurement_qubits),
                             do_swaps=False).inverse(),
                         measurement_qubits)

def measure(qc, n):
    qc.measure(n, n)


def period_finder(n, m, a):
    
    # set up quantum circuit
    qc = QuantumCircuit(n+m, n)
    
    # initialize the qubits
    initialize_qubits(qc, n, m)
    qc.barrier()

    # apply modular exponentiation
    modular_exponentiation(qc, n, m, a)
    qc.barrier()

    # apply inverse QFT
    apply_iqft(qc, range(n))
    qc.barrier()

    # measure the n measurement qubits
    measure(qc, range(n))
    
    return qc


def rsa_page():
    import random
    N = 15

    a = randint(2, N) # 1 < a < 

    el = [2,7,8,11,13]
    a = random.choice(el)

    if gcd(a, N) == 1: # a shares no factors
        print(f"{1} < {a} < {N}, {1 < a < N}")
    else: # a shares a factor
        P = gcd(a, N)
        Q = N // gcd(a, N)
        print(f"P = {P}\nQ = {Q}\n\n",
            f"{P} x {Q} = {N}, {P * Q == N}\n")

    n = 4; m = 4

    qc = period_finder(n, m, a)
    # qc.draw(output='mpl')

    simulator = Aer.get_backend('qasm_simulator')
    counts = execute(qc, backend=simulator).result().get_counts(qc)

    # plot_histogram(counts)
    print(counts)
    counts_dec = sorted([int(measured_value[::-1], 2)
                     for measured_value in counts])
    print(counts_dec)

    print("Measured periods:", end='\t')
    for measured_value in counts_dec:
        print(measured_value, end='\t')
        
    print(measured_value)
        #     sort through the possible exponents, finding those which satisfy two constraints:

        # the exponent, x, must be even and
        # a^(x/2) + 1 ≠ 0 (mod N)
# convert and add binary periods to list
    counts_dec = sorted([int(measured_value[::-1], 2)
                        for measured_value in counts])
    print(counts_dec)

    print("Measured periods:", end='\t')
    for measured_value in counts_dec:
        print(measured_value, end='\t')
    print(measured_value)
    # with period, x, you can find nontrivial factors, P and Q , of N with gcd(a^(x/2) ± 1, N) .
    factors = set()

    for x in counts_dec:
        guesses = [gcd(int((a ** (x/2))) + 1, N),
                gcd(int((a ** (x/2))) - 1, N)]
        for guess in guesses:
            # ignore trivial factors
            if guess != 1 and guess != N and N % guess == 0:
                factors.add(guess)

    if len(factors):
        P = factors.pop()
        Q = factors.pop() if len(factors) else N // P
        print(f"P = {P}\nQ = {Q}\n\n",
            f"{P} x {Q} = {N}, {P * Q == N}")
    else:
        P, Q = rsa_page()
    return P, Q

@csrf_exempt
def coding_decoding(request):
    code = request.POST['input']
    P, Q = rsa_page()
    _, priv_key = rsa(P, Q)
    print("Using RSA and Shor's Algorithm,",
        f"you determine the private key to be:\n\t{priv_key}")
    
    dec_str = dec(code, priv_key)
    print(f"The decrypted word is {dec_str}!")  

    response = {'priv_key':str(priv_key),'dec_str':dec_str}  
    # print(response, type(priv_key), type(dec_str))
    return JsonResponse(response)


# perform business logic

from base.utils.backend import *
from base.utils.backend_eve import *
@csrf_exempt
def encrypt(request):
    data = request.body.decode('ascii')
    data = request.FILES['upload'].read().decode('ascii')
    print(data)
    sender_key = data.split('[')[1].split(']')[0].split(',')
    print(len(sender_key),sender_key)
    msg = randint(2, size=len(sender_key))
    print('msg',[int(m) for m in msg])
    # msg =  data['msg']
    results = []
    for i in range(len(sender_key)):
        if(int(sender_key[i])==1 and int(msg[i])==1):
            results.append(0)
        if(int(sender_key[i])==1 and int(msg[i])==0):
            results.append(1)
        if(int(sender_key[i])==0 and int(msg[i])==1):
            results.append(1)
        if(int(sender_key[i])==0 and int(msg[i])==0):
            results.append(0)
    # print(results)
    return JsonResponse({'encrypted_msg':results,'msg':[int(m) for m in msg]})

@csrf_exempt
def decrypt(request):
    # data = request.body.decode('ascii')
    data = request.FILES['upload'].read().decode('ascii')
    print(data)
    receiver_key = data.split('[')[1].split(']')[0].split(',')
    msg =  request.POST.getlist('msg')
    print('msg',msg)
    # msg = msg['msg']
    results = []
    for i in range(len(receiver_key)):
        if(int(receiver_key[i])==1 and int(msg[i])==1):
            results.append(0)
        if(int(receiver_key[i])==1 and int(msg[i])==0):
            results.append(1)
        if(int(receiver_key[i])==0 and int(msg[i])==1):
            results.append(1)
        if(int(receiver_key[i])==0 and int(msg[i])==0):
            results.append(0)
    print(results)
    return JsonResponse({'decrypt_msg':results})
    
@csrf_exempt
def eve_poc(request):
    n = int(request.POST['size'])
    message,sender_bit,sender_base = sender_bits(n)
    intercepted_message = eve(n,message)
    receiver_results,receiver_base = receiver_bits(n,message)
    sample_size = 15
    bit_selection = randint(n, size=sample_size)
    _sender_key = sender_key(sender_base, receiver_base, sender_bit,n)
    _receiver_key = receiver_key(sender_base, receiver_base, receiver_results,n)
    receiver_sample = safety_check(_receiver_key, bit_selection)
    print("  receiver_sample = " + str(receiver_sample))
    sender_sample = safety_check(_sender_key, bit_selection)
    print("sender_sample = "+ str(sender_sample))
    status = compare(sender_sample,receiver_sample)
    sender_base_new = []
    receiver_base_new = []
    for i in range(len(sender_base)):
        if int(sender_base[i])==0:
            sender_base_new.append('z')
        else:
            sender_base_new.append('x')
    for i in range(len(receiver_base)):
        if int(receiver_base[i])==0:
            receiver_base_new.append('z')
        else:
            receiver_base_new.append('x')
    context = json.dumps({'sender_bits':[int (s) for s in sender_bit],'sender_base':sender_base_new,'receiver_base':receiver_base_new,'intercepted_message':[str(m) for m in intercepted_message],'status':str(status),'sender_key':[int (s) for s in _sender_key],'sender_sample':[int (s) for s in sender_sample],'receiver_key':[int (s) for s in _receiver_key],'receiver_sample':[int (s) for s in receiver_sample],'receiver_data':[int (s) for s in receiver_results],'sender_data':[int (s) for s in sender_bit],'n':int(n)})
    return JsonResponse({'context':context})



@csrf_exempt

def safe_poc(request):

    import json

    print(request.POST['size'])

    n = int(request.POST['size'])

    message,sender_bit,sender_base = sender_bits(n)

    receiver_results,receiver_base = receiver_bits(n,message)

       

    receiver_sample,receiver_key = receiver_check(sender_base, receiver_base, receiver_results,n)

    sender_sample,sender_key = sender_check(sender_base, receiver_base, sender_bit,n)

    status = compare(sender_sample,receiver_sample)

    # context = {'status':status,'sender_key':sender_key,'sender_sample':sender_sample,'receiver_key':receiver_key,'receiver_sample':receiver_sample,'receiver_results':receiver_results,'message':message,'sender_bit':sender_bit,'sender_base':sender_base,'n':int(n)}

    # context = json.dumps({'message':str(message),'status':str(status),'sender_key':[int (s) for s in sender_key],'sender_sample':[int (s) for s in sender_sample],'receiver_key':[int (s) for s in receiver_key],'receiver_sample':[int (s) for s in receiver_sample],'receiver_results':[int (s) for s in receiver_results],'sender_bits':[int (s) for s in sender_bit],'sender_base':[int (s) for s in sender_base],'n':int(n)})
    print({'sender_base':sender_base,'receiver_base':receiver_base})
    sender_base_new = []
    receiver_base_new = []
    for i in range(len(sender_base)):
        if int(sender_base[i])==0:
            sender_base_new.append('z')
        else:
            sender_base_new.append('x')
    for i in range(len(receiver_base)):
        if int(receiver_base[i])==0:
            receiver_base_new.append('z')
        else:
            receiver_base_new.append('x')
    context = json.dumps({'sender_bit':[int (s) for s in sender_bit],'sender_base':sender_base_new,'receiver_base':receiver_base_new,'message':str(message),'status':str(status),'sender_key':[int (s) for s in sender_key],'receiver_key':[int (s) for s in receiver_key],'sender_sample':[int (s) for s in sender_sample],'receiver_sample':[int (s) for s in receiver_sample],'receiver_data':[int (s) for s in receiver_results],'sender_data':[int (s) for s in sender_bit],'n':int(n)})

    print(context)

    return JsonResponse({"context":context})

 

@csrf_exempt

def restart(request):

    file = open("measurements_R.txt","w")

    file.close()

    file = open("measurements_S.txt","w")

    file.close()

    file = open("data_R.txt","w")

    file.close()

    file = open("data_S.txt","w")

    file.close()

    return JsonResponse({"status":"Success"})

 

@csrf_exempt

def receiver(request):

 

    file = open("measurements_R.txt", "a+")

    file.seek(0)

    content = file.read()

    print(content)

 

    M = ["x", "z"]

    print(random.choice(M))

    M = random.choice(M)

 

    content = f"\n{M}"

    file.write(content)

    file.close()

    # response = json.loads(request.text)

    response = request.POST

    Q = response["bit"][0]

    qc = QuantumCircuit(1)

   

    print(response)

    sim = Aer.get_backend("aer_simulator")

 

    if M == "x":

        print("INT Q:  ",int(Q))

        qc.x(int(Q))

        qc.draw()

       

        qc.save_statevector()

        qobj = assemble(qc)

        state = sim.run(qobj).result().get_statevector()

        # print(state)    

        # plot_bloch_multivector(state)

    else:

        print("INT Q:  ",int(Q))

        qc.z(int(Q))

        qc.draw()

       

        qc.save_statevector()

        qobj = assemble(qc)

        state = sim.run(qobj).result().get_statevector()

        # print(state)

        # plot_bloch_multivector(state)

    print(str(state))

    R = str(state).split("[")[1].split("]")[0].split(",")[1].split(".")[0]

    print('R',R)

    file = open("data_R.txt", "a+")

    file.seek(0)

    content = file.read()

    print(content)

    content = f"\n{R}"

    file.write(content)

    file.close()

 

    return JsonResponse({"resp":"1"})

 

@csrf_exempt

def sender(request):

   

    file = open("measurements_S.txt", "a+")

    file.seek(0)

    content = file.read()

    print(content)

 

    M = ["x", "z"]

    print(random.choice(M))

    M = random.choice(M)

 

    content = f"\n{M}"

    file.write(content)

    file.close()

 

    response = request.POST

    sim = Aer.get_backend("aer_simulator")

    Q = response["bit"][0]

    qc = QuantumCircuit(1)

   

    print(response)

 

    if M == "x":

        print("INT Q:  ",int(Q))

        qc.x(int(Q))

        qc.draw()

       

        qc.save_statevector()

        qobj = assemble(qc)

        state = sim.run(qobj).result().get_statevector()

        # print(state)    

        # plot_bloch_multivector(state)

    else:

        qc.z(0)

        qc.draw()

       

        qc.save_statevector()

        qobj = assemble(qc)

        state = sim.run(qobj).result().get_statevector()

        # print(state)

        # plot_bloch_multivector(state)

    print(str(state))

    S = str(state).split("[")[1].split("]")[0].split(",")[1].split(".")[0]

    print('S',S)

    file = open("data_S.txt", "a+")

    file.seek(0)

    content = file.read()

    print(content)

    content = f"\n{S}"

    file.write(content)

    file.close()

 

    return JsonResponse({"resp":"1"})

 

# @csrf_exempt

# def compare(request):

#     # data = request.body

#     data = request.POST

#     print(data)

#     with open("measurements_S.txt") as file:

#         file = file.readlines()

#         MS = [f.replace("\n","") for f in file]

#         print(MS)

#     with open("measurements_R.txt") as file:

#         file = file.readlines()

#         MR = [f.replace("\n","") for f in file]

#         print(MR)

#     i=0

#     print(MR,MS)

#     common_ground = []

#     while(i<int(data["size"])):

#         if(MR[i]==MS[i]):

#             common_ground.append(i)

#         i=i+1

#     size = len(common_ground)

#     compare = []

#     common_ground_control = common_ground

#     for s in range(round(size/4)):

#         choice = random.choice(common_ground)

#         compare.append(choice)
