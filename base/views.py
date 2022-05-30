from django.shortcuts import render
from qiskit.visualization import plot_bloch_multivector, plot_histogram
import requests as req
from django.http import JsonResponse
from qiskit import QuantumCircuit, assemble, Aer
import random
import json
from django.views.decorators.csrf import csrf_exempt
measurements = []
data = []
# perform business logic
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
    response = json.loads(request.content)
    Q = response["bit"]
    qc = QuantumCircuit(1)
    
    print(response)
    sim = Aer.get_backend("aer_simulator")

    if M == "x":
        qc.x(Q)
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
    
    R = str(state).split("[")[1].split("]")[0].split(",")[1].split(".")[0]
    
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

    response = request.data
    Q = response["bit"]
    qc = QuantumCircuit(1)
    
    print(response)
    sim = Aer.get_backend("aer_simulator")

    if M == "x":
        qc.x(Q)
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
    
    S = str(state).split("[")[1].split("]")[0].split(",")[1].split(".")[0]
        
    file = open("data_S.txt", "a+")
    file.seek(0)
    content = file.read()
    print(content)
    content = f"\n{S}"
    file.write(content)
    file.close()

    return JsonResponse({"resp":"1"})

@csrf_exempt
def compare(request):
    # data = request.body
    data = request.body
    print(data)
    with open("measurements_S.txt") as file:
        file = file.readlines()
        MS = [f.replace("\n","") for f in file]
        print(MS)
    with open("measurements_R.txt") as file:
        file = file.readlines()
        MR = [f.replace("\n","") for f in file]
        print(MR)
    i=0
    common_ground = []
    while(i<data["size"]):
        if(MR[i]==MS[i]):
            common_ground.append(i)
        i=i+1
    size = len(common_ground)
    compare = []
    common_ground_control = common_ground
    for s in range(round(size/4)):
        choice = random.choice(common_ground)
        compare.append(choice)
        common_ground.remove(choice)
    crypto_key_ind = [item for item in common_ground_control if item not in compare]
    
    with open("data_S.txt") as file:
        file = file.readlines()
        DS = [f.replace("\n","") for f in file]
        print(DS)
    with open("data_R.txt") as file:
        file = file.readlines()
        DR = [f.replace("\n","") for f in file]
        print(DR)

        compare_data_R,compare_data_S,compare_msg,cryptokey_data_R,cryptokey_data_d, cryptokey_msg = ([] for i in range(5))

    for i in range(len(compare)):
        compare_data_R.append(DR[compare[i]])
        compare_data_S.append(DS[compare[i]])
        compare_msg.append(MR[compare[i]])
    for i in range(len(crypto_key_ind)):
        cryptokey_data_R.append(DR[crypto_key_ind[i]])
        cryptokey_data_d.append(DR[crypto_key_ind[i]])
        cryptokey_msg.append(MR[crypto_key_ind[i]])


    return JsonResponse({"compare":compare,"cryptographic":crypto_key_ind,"compare_data_R":compare_data_R,"compare_data_S":compare_data_S,"compare_msg":compare_msg,"cryptokey_data_R":cryptokey_data_R,"cryptokey_data_d":cryptokey_data_d,"cryptokey_msg":cryptokey_msg})




