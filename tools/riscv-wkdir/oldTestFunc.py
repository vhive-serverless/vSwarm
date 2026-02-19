import subprocess
import time

# Define the image name of your function
import sys
import argparse
import os

# events = [["L1-dcache-load-misses", "L1-dcache-store"],["L1-icache-load-misses", "LLC-load-misses"], ["dTLB-load-misses", "iTLB-load-misses"], ["cpu-cycles", "instructions"]]
# events = [["cpu-cycles", "instructions"],["L1-dcache-load-misses", "L1-dcache-store"]] #,["L1-icache-load-misses", "LLC-load-misses"], ["dTLB-load-misses", "iTLB-load-misses"], ["core_clock_cycles", "instructions_retired"]]
# events = [["instructions:u", "instructions:k"],["cpu-cycles:k","cpu-cycles:u"]]
# events = [["cpu-cycles:k", "instructions:k"],["cpu-cycles:u","instructions:u"]]
events = [["duration_time","instructions"]]
# ,["instructions","system_time"]]
# ,["instructions:u", "instructions:k"],["cpu-cycles:k","cpu-cycles:u"]]

# geo-search database_geo rate-search database_rate
hotelApp = ["geo","rate", "profile", "recommendation", "reservation","user","search"]
hotelApp = ["geo","rate", "profile", "recommendation", "reservation","user"]
# "search"]
# redis for cartService
onlineShopApp = ["recommendationservice", "productcatalogservice", "currencyservice", "paymentservice", "shippingservice", "emailservice", "adservice", "cartservice"]
# , "checkoutservice"]
standaloneOld = ["fibonacci-go", "fibonacci-nodejs", "fibonacci-python", "aes-go", "aes-nodejs", "aes-python", "auth-go", "auth-nodejs", "auth-python"]
mediaHandling = ["image-rotate", "video-analytics-standalone", "compression", "video-processing"]
standaloneNew = ["bert-python", "gptj-python", "rnn-serving-python", "sleeping-go", "spinning-go"]
standaloneNew = [ "gptj-python", "rnn-serving-python", "sleeping-go", "spinning-go"]
dbDependency = hotelApp + mediaHandling
functionList =  onlineShopApp + standaloneOld + hotelApp + standaloneNew + mediaHandling
functionList =  onlineShopApp + standaloneOld  + standaloneNew 
functionList = mediaHandling
specialFunctions = {"cartservice":"redis"}

def bootInitDatabaseFunc(functionName, functionYaml="./functions.yaml"):
    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "init-"+functionName+"-database"])
    result = subprocess.run(["docker","wait","init-"+functionName+"-database"],stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True)
    output = result.stdout
    if output!="0":
        print(output)
    return -1
    subprocess.run(["docker","rm","init-"+functionName+"-database"])
                


def functionListHasDbDependency():
    for func in functionList:
        if func in dbDependency :
            return True
    return False

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--function", type = str, default="fibonacci-go")
    parser.add_argument("-o", "--output", type = str, default="finalTests")
    parser.add_argument("-t", "--times", type = int, default=10, help="Number of times to run the function")
    return parser.parse_args()



def main():
    args = parse_arguments()
    output = args.output
    times = args.times
    if not os.path.exists(output):
        os.makedirs(output)
    else:
        print(f"Do you want to overwrite the existing output folder {output}? (y/n)")
        response = input().strip().lower()
        if response == 'y':
            subprocess.run(["rm", "-rf", output])
            os.makedirs(output)

    print("Starting Base Results Collection...")
    BaseResults(output, times)
    print("Finished Base Results Collection.")


def BaseResults(output, times):
    outputExperiment = output + "/BaseResults/"
    if os.path.exists(outputExperiment):
        subprocess.run(["rm", "-rf", outputExperiment])
    os.makedirs(outputExperiment)
    # if functionListHasDbDependency():
    #     bootCassandraAndMMC()
    searchFuncFlag= False
    # if "search" in functionList:
    #     searchFuncFlag=True
    #     functionList.remove("search")

    for function in functionList:
        if function in mediaHandling:
            bootInitDatabaseFunc(function)
        for event1, event2 in events:
            outputEvent = outputExperiment + event1 + "-" + event2
            if  os.path.exists(outputEvent):
                subprocess.run(["rm", "-rf", outputEvent])
            os.makedirs(outputEvent)        
            run_functionSimple(function, times, outputEvent, event1, event2)
    # if functionListHasDbDependency():
    #     shutdownCassandra()
    # # shutdownCassandra()
    # if searchFuncFlag:
    #     bootCassandraAndMMC(isSearch=True)
    #     for event1, event2 in events:
    #         outputEvent = outputExperiment + event1 + "-" + event2  
    #         run_functionSimple("search", times, outputEvent, event1, event2)
    #     shutdownCassandra(isSearch=True)
    print("Base results collected.")

def bootCassandraAndMMC(functionYaml="./functions.yaml", isSearch= False):
    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "database"])
    subprocess.run(["docker", "update", "db", "--cpuset-cpus", "1"])

    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "memcached"])
    subprocess.run(["docker", "update", "mmc", "--cpuset-cpus", "2"])

    waitForCassandra()


def shutdownCassandra( isSearch= False):

    # if isSearch :

    subprocess.run(["docker", "stop", "db"])
    subprocess.run(["docker", "rm", "db"])
    subprocess.run(["docker", "stop", "mmc"])
    subprocess.run(["docker", "rm", "mmc"]) 

def getServerExactAddress(name):
    while True:
        try:
            # Run the command and capture the output
            result1 = subprocess.run(
                ["docker", "logs", "gptj-python"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = result1.stdout + result1.stderr

            # Check for 'UN' (Up and Normal) in output
            if "Start" in output:
                break


        except Exception as e:
            print(f"\n Error while checking GPTJ-PYTHON CONTAINER status: {e}\n")

        time.sleep(5)
    result = subprocess.run(
        [
            "docker",
            "inspect",
            "-f",
            "{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
            name,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip() 



def run_functionSimple(function, times, output, event1, event2, functionYaml="./functions.yaml"):
    # print(f"Testing: {function} ")
    for i in range(times):
        subprocess.run(["docker-compose", "-f",functionYaml, "up" , "-d", function])
        # subprocess.run(["docker", "update", function, "--cpuset-cpus", "3"])
        if function == "recommendationservice":
            subprocess.run(["docker-compose", "-f",functionYaml, "up" , "-d", "prod-cat-dependent"])
            subprocess.run(["docker", "update", "prod-cat-dependent", "--cpuset-cpus", "3"])
        print(f"Performing request to {function}-server...")
        n_invocations = 10
        n_warming = 0   
        time.sleep(10)
                # "./clientPerf",
        # subprocess.run(["taskset","-c","0",
        if "ing-go" in function:
            subprocess.run([
                "./client",
                "-function-name", "aes-go",
                "-url", "localhost",
                "-port", "50000",
                # "-event1", event1,
                # "-event2", event2,
                "-n", str(n_invocations),
                "-w", str(n_warming),
                "-input", "10",
                # "-latency-output", f"./{output}/{function}.txt"
            ])
        elif function in mediaHandling:
            subprocess.run([
                "./client",
                "-function-name", function,
                "-url", "localhost",
                "-port", "50000",
                # "-event1", event1,
                # "-event2", event2,
                "-n", str(n_invocations),
                "-w", str(n_warming),
                # "-latency-output", f"./{output}/{function}.txt"
            ]) 
        elif function == "gptj-python":
            exactAddress = getServerExactAddress(function)
            subprocess.run([
                "./client",
                "-function-name", function,
                "-url", exactAddress,
                "-port", "50051",
                # "-event1", event1,
                # "-event2", event2,
                "-n", str(n_invocations),
                "-w", str(n_warming),
                # "-latency-output", f"./{output}/{function}.txt"
            ])        
        else:
            subprocess.run([
                    "./client",
                    "-function-name", function,
                    "-url", "localhost",
                    "-port", "50000",
                    # "-event1", event1,
                    # "-event2", event2,
                    # "-n", str(n_invocations),
                    # "-w", str(n_warming),
                    "-input", "10",
                    # "-latency-output", f"./{output}/{function}.txt"
                ])

        subprocess.run(["docker", "stop", function])
        subprocess.run(["docker", "rm", function])
        if function == "recommendationservice":
            subprocess.run(["docker", "stop", "prod-cat-dependent"])
            subprocess.run(["docker", "rm", "prod-cat-dependent"]) 

def waitForCassandra():
    while True:
        try:
            # Run the command and capture the output
            result = subprocess.run(
                ["docker", "exec", "db", "bash", "-c", "nodetool status"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = result.stdout

            # Check for 'UN' (Up and Normal) in output
            if "UN" in output:
                print("\n Cassandra is Up and Normal!\n")
                break
            else:
                print("\n Cassandra not ready yet... retrying in 1 minute.\n")

        except Exception as e:
            print(f"\n Error while checking Cassandra status: {e}\n")

        time.sleep(60)

     







def run_functionWithStressSeperate(function, times, output, event1, event2):
    print(f"Testing: {function} ")
    for i in range(times):
        subprocess.run(["docker-compose", "-f", "./functions.yaml", "up" , "-d", function])
        subprocess.run(["docker", "update", function, "--cpuset-cpus", "3"])
        if function == "recommendationservice":
            subprocess.run(["docker-compose", "-f", "./functions.yaml", "up" , "-d", "prod-cat-dependent"])
            subprocess.run(["docker", "update", "prod-cat-dependent", "--cpuset-cpus", "3"])
        print(f"Performing request to {function}-server...")
        n_invocations = 10
        n_warming = 0   
        # taskset -c 1,2 stress-ng --cpu 2
        stressProcess = subprocess.Popen(["taskset", "-c", "1,2",
                "stress-ng", "--cache", "2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Wait for stress-ng to start
                # "./clientPerf",
        subprocess.run(["taskset","-c","0",
                "./clientPerf",
                "-function-name", function,
                "-url", "localhost",
                "-port", "50000",
                "-event1", event1,
                "-event2", event2,
                "-n", str(n_invocations),
                "-w", str(n_warming),
                "-input", "10",
                "-latency-output", f"./{output}/{function}.txt"
            ])
        stressProcess.terminate()  # Stop the stress-ng process
        stressProcess.wait()  # Wait for the process to finish
        
        subprocess.run(["docker", "stop", function])
        subprocess.run(["docker", "rm", function])
        if function == "recommendationservice":
            subprocess.run(["docker", "stop", "prod-cat-dependent"])
            subprocess.run(["docker", "rm", "prod-cat-dependent"]) 
                
def run_functionWithStress(function, times, output1, output2, event1, event2):
    print(f"Testing: {function} ")
    for i in range(times):
        subprocess.run(["docker-compose", "-f", "./functions.yaml", "up" , "-d", function])
        subprocess.run(["docker", "update", function, "--cpuset-cpus", "3"])
        if function == "recommendationservice":
            subprocess.run(["docker-compose", "-f", "./functions.yaml", "up" , "-d", "prod-cat-dependent"])
            subprocess.run(["docker", "update", "prod-cat-dependent", "--cpuset-cpus", "3"])
        print(f"Performing request to {function}-server...")
        n_invocations = 10
        n_warming = 0   
        # taskset -c 1,2 stress-ng --cpu 2
       
                # "./clientPerf",
        subprocess.run(["taskset","-c","0",
                "./clientPerf",
                "-function-name", function,
                "-url", "localhost",
                "-port", "50000",
                "-event1", event1,
                "-event2", event2,
                "-n", str(n_invocations),
                "-w", str(n_warming),
                "-input", "10",
                "-latency-output", f"./{output1}/{function}.txt"
            ])
        subprocess.run(["taskset", "-c", "3",
                "stress-ng", "--cache", "1", "--timeout", "10s"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskset","-c","0",
                "./clientPerf",
                "-function-name", function,
                "-url", "localhost",
                "-port", "50000",
                "-event1", event1,
                "-event2", event2,
                "-n", str(n_invocations),
                "-w", str(n_warming),
                "-input", "10",
                "-latency-output", f"./{output2}/{function}.txt"
            ])
        subprocess.run(["docker", "stop", function])
        subprocess.run(["docker", "rm", function])
        if function == "recommendationservice":
            subprocess.run(["docker", "stop", "prod-cat-dependent"])
            subprocess.run(["docker", "rm", "prod-cat-dependent"])

def run_functionDropCaches(function, times, output, event1, event2):
    # print(f"Testing: {function} ")
    for i in range(times):


        subprocess.run(["docker-compose", "-f", "./functions.yaml", "up" , "-d", function])
        subprocess.run(["docker", "update", function, "--cpuset-cpus", "3"])
        if function == "recommendationservice":
            subprocess.run(["docker-compose", "-f", "./functions.yaml", "up" , "-d", "prod-cat-dependent"])
            subprocess.run(["docker", "update", "prod-cat-dependent", "--cpuset-cpus", "3"])
        # drop caches
        subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"])

        print(f"Performing request to {function}-server...")
        n_invocations = 10
        n_warming = 0   
         
                # "./clientPerf",
        subprocess.run(["taskset","-c","0",
                "./clientPerf",
                "-function-name", function,
                "-url", "localhost",
                "-port", "50000",
                "-event1", event1,
                "-event2", event2,
                "-n", str(n_invocations),
                "-w", str(n_warming),
                "-input", "10",
                "-latency-output", f"./{output}/{function}.txt"
            ])

        subprocess.run(["docker", "stop", function])
        subprocess.run(["docker", "rm", function])
        if function == "recommendationservice":
            subprocess.run(["docker", "stop", "prod-cat-dependent"])
            subprocess.run(["docker", "rm", "prod-cat-dependent"]) 




def SeccompResults(output,times):
    outputExperiment = output + "/SeccompResults/"
    if os.path.exists(outputExperiment):
        subprocess.run(["rm", "-rf", outputExperiment])
    os.makedirs(outputExperiment)
    bootCassandraAndMMC("./functionsSeccomp.yaml")
    for event1, event2 in events:
        outputEvent = outputExperiment + event1 + "-" + event2
        if  os.path.exists(outputEvent):
            subprocess.run(["rm", "-rf", outputEvent])
        os.makedirs(outputEvent)        
        for function in functionList:
            run_functionSimple(function, times, outputEvent, event1, event2, "./functionsSeccomp.yaml")
    shutdownCassandra()
    print("Seccomp results collected.")

def THP_EnabledResults(output, times):
    outputExperiment = output + "/THP_EnabledResults/"
    if os.path.exists(outputExperiment):
        subprocess.run(["rm", "-rf", outputExperiment])
    os.makedirs(outputExperiment)
    subprocess.run(["sudo", "sh", "-c", "echo always > /sys/kernel/mm/transparent_hugepage/enabled"])
    bootCassandraAndMMC()  

    for event1, event2 in events:
        outputEvent = outputExperiment + event1 + "-" + event2
        if  os.path.exists(outputEvent):
            subprocess.run(["rm", "-rf", outputEvent])
        os.makedirs(outputEvent)        
        for function in functionList:
            run_functionSimple(function, times, outputEvent, event1, event2)
    shutdownCassandra()
    subprocess.run(["sudo", "sh", "-c", "echo never > /sys/kernel/mm/transparent_hugepage/enabled"])
    print("THP enabled results collected.")

def StressSeparateResults(output, times):
    outputExperiment = output + "/StressSeparateResults/"
    if os.path.exists(outputExperiment):
        subprocess.run(["rm", "-rf", outputExperiment])
    os.makedirs(outputExperiment)

    bootCassandraAndMMC()
    for event1, event2 in events:
        outputEvent = outputExperiment + event1 + "-" + event2
        if  os.path.exists(outputEvent):
            subprocess.run(["rm", "-rf", outputEvent])
        os.makedirs(outputEvent)        
        for function in functionList:
            run_functionWithStressSeperate(function, times, outputEvent, event1, event2)
    shutdownCassandra()
    print("Stress separate results collected.")

def StressOnCoreResults(output, times):
    outputExperiment = output + "/StressOnCoreResults/"
    if os.path.exists(outputExperiment):
        subprocess.run(["rm", "-rf", outputExperiment])
    os.makedirs(outputExperiment)

    bootCassandraAndMMC()
    for event1, event2 in events:
        outputEvent1 = outputExperiment + event1 + "-" + event2
        outputEvent2 = outputExperiment + event1 + "-" + event2 + "-stressed"
        if  os.path.exists(outputEvent1):
            subprocess.run(["rm", "-rf", outputEvent1])
        os.makedirs(outputEvent1)        

        if  os.path.exists(outputEvent2):
            subprocess.run(["rm", "-rf", outputEvent2])
        os.makedirs(outputEvent2)        

        for function in functionList:
            run_functionWithStress(function, times, outputEvent1,outputEvent2 , event1, event2)
    shutdownCassandra()
    print("Stress on core results collected.")

def DropCachesResults(output, times):
    outputExperiment = output + "/DropCachesResults/"
    if os.path.exists(outputExperiment):
        subprocess.run(["rm", "-rf", outputExperiment])
    os.makedirs(outputExperiment)
    bootCassandraAndMMC()
    for event1, event2 in events:
        outputEvent = outputExperiment + event1 + "-" + event2
        if  os.path.exists(outputEvent):
            subprocess.run(["rm", "-rf", outputEvent])
        os.makedirs(outputEvent)        
        for function in functionList:
            run_functionDropCaches(function, times, outputEvent, event1, event2)
    shutdownCassandra()
    print("Drop caches results collected.")




if __name__ == "__main__":
    main()



