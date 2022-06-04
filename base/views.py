from django.shortcuts import render

from qiskit.visualization import plot_bloch_multivector, plot_histogram

import requests as req

from django.http import JsonResponse

import random

import json

from django.views.decorators.csrf import csrf_exempt

measurements = []

data = []

# perform business logic

from base.utils.backend import *
from base.utils.backend_eve import *

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
