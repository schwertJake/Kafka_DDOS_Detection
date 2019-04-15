from datetime import datetime
import time
import operator
import visualize

def parse_apache_log_line(log_line: str) -> dict:
    split_ws = log_line.split(" ")
    return {
        "IP": split_ws[0],
        "Time": get_time_epoch(split_ws[3][1:], split_ws[4][:-1]),
        "Request_Method": split_ws[5][1:],
        "Request_Resource": split_ws[6],
        "Request_Protocol": split_ws[7][:-1],
        "Status_Code": int(split_ws[8]),
        "Payload_Size": int(split_ws[9]),
        "Referer": split_ws[10].replace("\"", ""),
        "User_Agent": " ".join(split_ws[11:-1]).replace("\"", "")
    }

def get_time_epoch(time_stamp: str, time_zone: str) -> float:
    d = datetime.strptime(time_stamp+" "+time_zone, "%d/%b/%Y:%H:%M:%S %z")
    return int(d.timestamp())

def ingest_and_parse(file_path: str):
    ret_dict = []
    start = time.time()
    with open(file_path) as file:
        for line in file:
            ret_dict.append(parse_apache_log_line(line))
    end = time.time()
    return ret_dict, end - start

def transform_data_ip_count(data: list):
    ret_dict = {}
    for line_data in data:
        if line_data["IP"] not in ret_dict.keys():
            ret_dict[line_data["IP"]] = 1
        else:
            ret_dict[line_data["IP"]] += 1
    return sorted(ret_dict.items(), key=operator.itemgetter(1))

def transform_ip_count_to_freq(ip_count_list):
    ret_dict = {}
    for val in ip_count_list:
        if val[1] not in ret_dict.keys():
            ret_dict[val[1]] = 1
        else:
            ret_dict[val[1]] += 1
    return list(ret_dict.items())

if __name__ == "__main__":
    parsed_data, time_taken = ingest_and_parse("apache-access-log.txt")
    ip_access_count = transform_data_ip_count(parsed_data)

    print("Total Time (s):", time_taken)
    print("Total Records:", len(parsed_data))
    print("Avg Records Per Second", len(parsed_data)/time_taken)

    visualize.plot(
        transform_ip_count_to_freq(
            ip_access_count
        )
    )