import subprocess
import time

# Define the image name of your function
import sys
import argparse
import os

events = [["cpu-cycles","instructions"],["L1-dcache-load-misses", "L1-dcache-store"]]
hotelApp = ["geo","rate", "profile", "recommendation", "reservation","user"]
extraFunctions = ["search","checkoutservice"]
onlineShopApp = ["recommendationservice", "productcatalogservice", "currencyservice", "paymentservice", "shippingservice", "emailservice", "adservice", "cartservice"]
standaloneOld = ["fibonacci-go", "fibonacci-nodejs", "fibonacci-python", "aes-go", "aes-nodejs", "aes-python", "auth-go", "auth-nodejs", "auth-python"]
mediaHandling = [  "compression", "video-processing","image-rotate","video-analytics-standalone"]
standaloneNew = ["bert-python", "gptj-python", "rnn-serving-python", "sleeping-go", "spinning-go"]
dbDependency = hotelApp + mediaHandling
functionList =  onlineShopApp  + standaloneOld + hotelApp + standaloneNew + mediaHandling +  extraFunctions 
heavyFunctions = ["video-analytics-standalone","video-processing","image-rotate","compression","bert-python","gptj-python", "rnn-serving-python","adservice"] + hotelApp
extraDependencyFunctions = {
    "cartservice": ("redis", "1"),
    "recommendationservice": ("prod-cat-dependent", "3"),
}
specialInputFunctions = { "video-analytics-standalone":"video1.mp4",
                    "video-processing":"video2.mp4",
                    "image-rotate":"img3.jpg",
                    "compression":"img3.jpg"
}
functionList = standaloneOld
runningClient="clientPerf"

def parse_arguments():
    parser = argparse.ArgumentParser()
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
    for event1, event2 in events:
        outputEvent = outputExperiment + event1 + "-" + event2
        if os.path.exists(outputEvent):
            subprocess.run(["rm", "-rf", outputEvent])
        os.makedirs(outputEvent) 
        if "search" in functionList:
            prepare_search()
            function = "search"
            for event1, event2 in events:       
                run_functionSimple(function, times, outputEvent, event1, event2)
            functionList.remove("search")
            clean_search()
        for function in functionList:
            if function in dbDependency:
                bootCassandraAndMMC()
            if function in mediaHandling:
                bootInitDatabaseFunc(function)
            run_functionSimple(function, times, outputEvent, event1, event2)
            if function in dbDependency:
                shutdownCassandra()
    print("Base results collected.")

def run_functionSimple(function, times, output, event1, event2, functionYaml="./functions.yaml"):
    for i in range(times):
        if function =="checkoutservice":
            run_checkoutservice(output, event1, event2, functionYaml)
            continue
        subprocess.run(["docker-compose", "-f",functionYaml, "up" , "-d", function])
        subprocess.run(["docker", "update", function, "--cpuset-cpus", "3"])
        if function in extraDependencyFunctions:
            extraFunc, pinnedCore = extraDependencyFunctions[function]
            subprocess.run(["docker-compose", "-f",functionYaml, "up" , "-d", extraFunc])
            subprocess.run(["docker", "update", "prod-cat-dependent", "--cpuset-cpus", pinnedCore])
        if function in heavyFunctions:
            waitForFunction(function)
        n_invocations = 10
        n_warming = 0  
        time.sleep(10)

        print(f"Performing request to {function}-server...")
        if "ing-go" in function:
            subprocess.run([
                f"./{runningClient}",
                "-function-name", "aes-go",
                "-url", "localhost",
                "-port", "50000",
                "-event1", event1,
                "-event2", event2,
                "-input", "10",
                "-n", str(n_invocations),
                "-w", str(n_warming),                
                "-latency-output", f"./{output}/{function}.txt"
            ])
        elif function in mediaHandling:
            subprocess.run([
                f"./{runningClient}",
                "-function-name", function+"-python",
                "-url", "localhost",
                "-port", "50000",
                "-event1", event1,
                "-event2", event2,                
                "-input",specialInputFunctions[function],
                "-n", str(n_invocations),
                "-w", str(n_warming) ,  
                 "-latency-output", f"./{output}/{function}.txt"
             
            ]) 
        else:
            subprocess.run([
                    f"./{runningClient}",
                    "-function-name", function,
                    "-url", "localhost",
                    "-port", "50000",
                    "-event1", event1,
                    "-event2", event2,
                    "-input", "10",
                    "-n", str(n_invocations),
                    "-w", str(n_warming),
                    "-latency-output", f"./{output}/{function}.txt"
                ])

        subprocess.run(["docker", "stop", function])
        subprocess.run(["docker", "rm", function])
        if function in extraDependencyFunctions:
            extraFunc, pinnedCore = extraDependencyFunctions[function]
            subprocess.run(["docker", "stop", extraFunc])
            subprocess.run(["docker", "rm", extraFunc]) 

def bootInitDatabaseFunc(functionName, functionYaml="./functions.yaml"):
    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "init-"+functionName+"-database"])
    result = subprocess.run(["docker","wait","init-"+functionName+"-database"],stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True)
    output = result.stdout
    subprocess.run(["docker","stop","init-"+functionName+"-database"])
    subprocess.run(["docker","rm","init-"+functionName+"-database"])
    if output!="0":
        print(output)
        return -1
                

def bootCassandraAndMMC(functionYaml="./functions.yaml"):
    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "database"])
    subprocess.run(["docker", "update", "db", "--cpuset-cpus", "1"])

    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "memcached"])
    subprocess.run(["docker", "update", "mmc", "--cpuset-cpus", "2"])

    waitForCassandra()


def shutdownCassandra( isSearch= False):

    subprocess.run(["docker", "stop", "db"])
    subprocess.run(["docker", "rm", "db"])
    subprocess.run(["docker", "stop", "mmc"])
    subprocess.run(["docker", "rm", "mmc"]) 





def run_checkoutservice(output, event1, event2, functionYaml="./functions.yaml"):
    depedent = ["shippingservice","productcatalogservice","cartservice","currencyservice","emailservice","paymentservice"]
    for function in depedent:
            subprocess.run(["docker-compose", "-f",functionYaml, "up" , "-d", function+"-checkout"])
            subprocess.run(["docker", "update", function+"-checkout", "--cpuset-cpus", "3"])
    subprocess.run(["docker-compose", "-f",functionYaml, "up" , "-d", "redis"])
    subprocess.run(["docker", "update", "redis", "--cpuset-cpus", "1"])            
    subprocess.run(["docker-compose", "-f",functionYaml, "up" , "-d", "checkoutservice"])
    subprocess.run(["docker", "update", "checkoutservice", "--cpuset-cpus", "3"])
    function = "checkoutservice"
    time.sleep(10)
    print(f"Performing request to checkoutservice-server...")
    n_invocations = 10
    n_warming = 0  
    subprocess.run([
            f"./{runningClient}",
            "-function-name", function,
            "-url", "localhost",
            "-port", "50000",
            "-event1", event1,
            "-event2", event2,
            "-input", "10",
            "-n", str(n_invocations),
            "-w", str(n_warming),
            "-latency-output", f"./{output}/{function}.txt"            
        ])
    subprocess.run(["docker", "stop",function])
    subprocess.run(["docker", "rm", function])
    subprocess.run(["docker", "stop","redis"])
    subprocess.run(["docker", "rm", "redis"])
    for function in depedent:
        subprocess.run(["docker", "stop", function+"-checkout"])
        subprocess.run(["docker", "rm", function+"-checkout"]) 


def prepare_search(functionYaml="./functions.yaml", isSearch= True):

    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "database_geo"])
    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "database_rate"])  

    subprocess.run(["docker", "update", "geo-db", "--cpuset-cpus", "1"])
    subprocess.run(["docker", "update", "rate-db", "--cpuset-cpus", "1"])

    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "memcached"])
    subprocess.run(["docker", "update", "mmc", "--cpuset-cpus", "2"])

    waitForCassandra("geo-db")
    waitForCassandra("rate-db")
    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "geo-search"])
    subprocess.run(["docker-compose", "-f", functionYaml, "up" , "-d", "rate-search"])  

    subprocess.run(["docker", "update", "geo-search", "--cpuset-cpus", "3"])
    subprocess.run(["docker", "update", "rate-search", "--cpuset-cpus", "3"])
    waitForFunction("geo-search")
    waitForFunction("rate-search")

def clean_search():
    subprocess.run(["docker","stop","rate-db"])    
    subprocess.run(["docker","rm","rate-db"])    
    subprocess.run(["docker","stop","geo-db"])
    subprocess.run(["docker","rm","geo-db"])
    subprocess.run(["docker","stop","mmc"])
    subprocess.run(["docker","rm","mmc"])
    subprocess.run(["docker","stop","geo-search"])
    subprocess.run(["docker","rm","geo-search"])
    subprocess.run(["docker","stop","rate-search"])
    subprocess.run(["docker","rm","rate-search"])


def waitForCassandra(db="db"):
    while True:
        try:
            result = subprocess.run(
                ["docker", "exec", db, "bash", "-c", "nodetool status"],
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

def waitForFunction(function):
    while True:
        try:
            result1 = subprocess.run(
                ["docker", "logs", function],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = result1.stdout + result1.stderr

            if "Start" in output or "listening" in output:
                break

        except Exception as e:
            print(f"\n Error while checking "+function+" status: {e}\n")
        time.sleep(5)



if __name__ == "__main__":
    main()
