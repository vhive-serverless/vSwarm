import sys
import statistics
import re
import os
# import numpy as np

hotelApp = ["geo","rate", "profile", "recommendation", "reservation","user"]
extraFunctions = ["search","checkoutservice"]
onlineShopApp = ["recommendationservice", "productcatalogservice", "currencyservice", "paymentservice", "shippingservice", "emailservice", "adservice", "cartservice"]
standaloneOld = ["fibonacci-go", "fibonacci-nodejs", "fibonacci-python", "aes-go", "aes-nodejs", "aes-python", "auth-go", "auth-nodejs", "auth-python"]
mediaHandling = [  "compression", "video-processing","image-rotate","video-analytics-standalone"]
standaloneNew = ["bert-python", "gptj-python", "rnn-serving-python", "sleeping-go", "spinning-go"]
dbDependency = hotelApp + mediaHandling
functionList =  onlineShopApp  + standaloneOld + hotelApp + standaloneNew + mediaHandling +  extraFunctions 

# events = [["cpu-cycles", "instructions"],["L1-dcache-load-misses", "L1-dcache-store"],["L1-icache-load-misses", "LLC-load-misses"], ["dTLB-load-misses", "iTLB-load-misses"]]

hotelAppMongo = ["geo_mongo","rate_mongo", "profile_mongo", "recommendation_mongo", "reservation_mongo","user_mongo"]
functionList = standaloneOld
# events = [["cpu-cycles", "instructions"]]
events = [["duration_time", "instructions"]]
events = [["cpu-cycles","instructions"],["L1-dcache-load-misses", "L1-dcache-store"]]

def get_scenario_list(directory):
    scenario_list = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and item not in scenario_list:
            scenario_list.append(item)
    scenario_list.sort()
    return scenario_list



def parse_perf_file(filename, event1, event2):
    event1_values = []
    event2_values = []
    coldFile = filename + "Cold.txt"
    warmFile = filename + "Warm.txt"
    with open(coldFile, 'r') as f:
        for line in f:
            # grab the leading number ONLY
            match = re.match(r'^\s*([\d,]+)', line)
            if not match:
                continue

            value = int(match.group(1).replace(',', ''))

            if event1 in line:
                event1_values.append(value)
            elif event2 in line:
                event2_values.append(value)
    coldEvent1 = int(statistics.median(event1_values))
    coldEvent2 = int(statistics.median(event2_values))
    # event1_values= np.array(event1_values)
    # event2_values = np.array(event2_values)
    # coldEvent1 = int(np.percentile(event1_values, 80))
    # coldEvent2 = int(np.percentile(event2_values, 80))
    # coldEvent1 = int(statistics.mean(event1_values))
    # coldEvent2 = int(statistics.mean(event2_values))
    event1_values = []
    event2_values = [] 
    with open(warmFile, 'r') as f:
        for line in f:
            # grab the leading number ONLY
            match = re.match(r'^\s*([\d,]+)', line)
            if not match:
                continue

            value = int(match.group(1).replace(',', ''))

            if event1 in line:
                event1_values.append(value)
            elif event2 in line:
                event2_values.append(value)

    warmEvent1 = int(statistics.median(event1_values))
    warmEvent2 = int(statistics.median(event2_values))
    # warmEvent1 = int(statistics.mean(event1_values))
    # warmEvent2 = int(statistics.mean(event2_values))
    # event1_values = np.array(event1_values)
    # event2_values = np.array(event2_values)
    # warmEvent1 = int(np.percentile(event1_values, 80))
    # warmEvent2 = int(np.percentile(event2_values, 80))
    return coldEvent1, coldEvent2, warmEvent1, warmEvent2


def format_with_dots(number):
    number = int(number)  # Truncate decimal part
    return f"{number:,}".replace(",", ".")


def write_to_file( scenario, scenario_results, output_file):
    with open(output_file, 'a') as f:
        f.write(f"{scenario}\n")
        header = "Function"
        for event1, event2 in events:
            if scenario == "StressOnCoreResults":
                header += f" \t {event1}Cold \t {event1}Warm \t {event1}-stressed-Cold \t {event1}-stressed-Warm \t {event2}Cold \t {event2}Warm \t {event2}-stressed-Cold \t {event2}-stressed-Warm"
            else:
                header += f" \t {event1}Cold \t {event1}Warm \t {event2}Cold \t {event2}Warm"
        f.write(header + "\n")
        
        for function in functionList:
            if function == "all":
                continue
            line = f"{function}"
            for event1, event2 in events:
                if scenario == "StressOnCoreResults":
                    coldEvent1, warmEvent1 = scenario_results[(function, event1)]
                    coldEvent2, warmEvent2 = scenario_results[(function, event2)]
                    coldEvent1_stressed, warmEvent1_stressed = scenario_results[(function, event1 + "-stressed")]
                    coldEvent2_stressed, warmEvent2_stressed = scenario_results[(function, event2 + "-stressed")]
                    line += f" \t {coldEvent1} \t {warmEvent1} \t {coldEvent1_stressed} \t {warmEvent1_stressed} \t {coldEvent2} \t {warmEvent2} \t {coldEvent2_stressed} \t {warmEvent2_stressed}"
                else:

                    coldEvent1, warmEvent1 = scenario_results[(function, event1)]
                    coldEvent2, warmEvent2 = scenario_results[(function, event2)]
                    line += f" \t {coldEvent1} \t {warmEvent1} \t {coldEvent2} \t {warmEvent2}"
                


            f.write(line + "\n")
        f.write("\n")
       
    



def main():
    if len(sys.argv) != 2:
        print("Usage: python3 perfAnalyze.py <directory> (e.g. results | no ./results )")
        return

    directory = sys.argv[1]
    scenario_list = get_scenario_list(directory)
    if not scenario_list:
        print(f"No scenarios found in directory: {directory}")
        return
    
    output_file = os.path.join(directory, "perfStats.txt")
    if os.path.exists(output_file):
        os.remove(output_file)
    os.makedirs(directory, exist_ok=True)
    for scenario in scenario_list:
        # if not(scenario == "StressOnCoreAfterResults" or scenario == "StressOnCoreResults"):
        #     continue
        scenario_path = os.path.join(directory, scenario)
        scenario_results = {}
        for event1, event2 in events:
            directory_event = os.path.join(scenario_path, event1 + "-" + event2)
            if not os.path.exists(directory_event):
                print(f"Directory {directory_event} does not exist.")
                continue
            for function in functionList:
                function_path = os.path.join(directory_event, function)
                if not os.path.exists(function_path + "Cold.txt") or not os.path.exists(function_path + "Warm.txt"):
                    print(f"Files for function {function} in {directory_event} do not exist.")
                    continue
                coldEvent1, coldEvent2, warmEvent1, warmEvent2 = parse_perf_file(function_path, event1, event2)
                scenario_results[(function, event1)] = (coldEvent1, warmEvent1)
                scenario_results[(function, event2)] = (coldEvent2, warmEvent2)

        if scenario == "StressOnCoreResults":
            for event1, event2 in events:
                directory_event = os.path.join(scenario_path, event1 + "-" + event2+"-stressed")
                if not os.path.exists(directory_event):
                    print(f"Directory {directory_event} does not exist.")
                    continue
                for function in functionList:
                    function_path = os.path.join(directory_event, function)
                    if not os.path.exists(function_path + "Cold.txt") or not os.path.exists(function_path + "Warm.txt"):
                        print(f"Files for function {function} in {directory_event} do not exist.")
                        continue
                    coldEvent1, coldEvent2, warmEvent1, warmEvent2 = parse_perf_file(function_path, event1, event2)
                    scenario_results[(function, event1+"-stressed")] = (coldEvent1, warmEvent1)
                    scenario_results[(function, event2+"-stressed")] = (coldEvent2, warmEvent2)
            # print(scenario, scenario_results)

  
        write_to_file(scenario, scenario_results, output_file)
                    


if __name__ == "__main__":
    main()

