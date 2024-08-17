import csv
import os
import numpy as np
from scipy.stats import mannwhitneyu

def parser_for_total_time(directory):
    file_dict = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open (file_path, "r") as infile:
                lines = infile.readlines()
            for line in lines:
                if line.startswith("> Total"):
                    time_str = line[11:]
                    time_list = time_str.split(" ")
                    if "hours" in time_str:
                        hours = time_list[0]
                        minutes = time_list[2]
                        seconds = time_list[5]
                    elif "minutes" in time_str:
                        hours = 0
                        minutes = time_list[0]
                        seconds = time_list[3]
                    break
            file_path_list = file_path.split("/")
            test_kind = file_path_list[6]
            seed =  file_path_list[7]
            project_name = file_path_list[8][0:-6]
            round = file_path_list[8][-5]
            test_kind_directory = "/home/whx/MutationTesting/Analysis/results/" + test_kind
            if not os.path.exists(test_kind_directory):
                os.makedirs(test_kind_directory)
            dictname = test_kind + "/" + project_name
            if test_kind_directory not in file_dict:
                file_dict[test_kind_directory] = set([dictname])
            else:
                file_dict[test_kind_directory].add(dictname)
            if dictname not in locals():
                locals()[dictname] = {"0":[None]*6,
                                      "2024":[None]*6,
                                      "99999":[None]*6}
            if hours == 0:
                locals()[dictname][seed][int(round)] = str(minutes) + "m" + str(seconds) + "s"
            else:
                locals()[dictname][seed][int(round)] = str(hours) + "h" + str(minutes) + "m" + str(seconds) + "s"
    for key in file_dict:
        for project in file_dict[key]:
            with open(project + ".csv", 'w') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Seed', 'Round 0', 'Round 1', 'Round 2', ' Round 3', 'Round 4', 'Round 5'])
                for seed, times in locals()[project].items():
                    csv_writer.writerow([seed] + times)

def significance_test(directory):
    file_dict = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open (file_path, "r") as infile:
                lines = infile.readlines()
            for line in lines:
                if line.startswith("> Total"):
                    time_str = line[11:]
                    time_list = time_str.split(" ")
                    if "hours" in time_str:
                        hours = time_list[0]
                        minutes = time_list[2]
                        seconds = time_list[5]
                    elif "minutes" in time_str:
                        hours = 0
                        minutes = time_list[0]
                        seconds = time_list[3]
                    break
            file_path_list = file_path.split("/")
            test_kind = file_path_list[6]
            seed =  file_path_list[7]
            project_name = file_path_list[8][0:-6]
            round = file_path_list[8][-5]
            test_kind_directory = "/home/whx/MutationTesting/Analysis/results/" + test_kind
            dictname = test_kind + "/" + project_name
            if test_kind_directory not in file_dict:
                file_dict[test_kind_directory] = set([dictname])
            else:
                file_dict[test_kind_directory].add(dictname)
            if dictname not in locals():
                locals()[dictname] = {"0":[None]*6,
                                      "2024":[None]*6,
                                      "99999":[None]*6}
            if hours == 0:
                locals()[dictname][seed][int(round)] = str(minutes) + "m" + str(seconds) + "s"
            else:
                locals()[dictname][seed][int(round)] = str(hours) + "h" + str(minutes) + "m" + str(seconds) + "s"
    for key in file_dict:
        u_test_values = []
        for project in file_dict[key]:
            for seed, times in locals()[project].items():
                project_name = project.split("/")[1]
                time_sec = []
                for time in times:
                    if "h" in time:
                        hours = int(time.split("h")[0])
                        minutes = int(time.split("h")[1].split("m")[0])
                        seconds = int(time.split("h")[1].split("m")[1].strip("s"))
                    else:
                        hours = 0
                        minutes = int(time.split("m")[0])
                        seconds = int(time.split("m")[1].strip("s"))
                    time_sec.append(hours*3600 + minutes*60 + seconds)
                if seed == "0":
                    seed_0 = np.array(time_sec)
                elif seed == "2024":
                    seed_2024 = np.array(time_sec)
                elif seed == "99999":
                    seed_99999 = np.array(time_sec)
            u_stat_0_vs_2024, p_val_0_vs_2024 = mannwhitneyu(seed_0, seed_2024)
            u_stat_0_vs_99999, p_val_0_vs_99999 = mannwhitneyu(seed_0, seed_99999)
            u_stat_2024_vs_99999, p_val_2024_vs_99999 = mannwhitneyu(seed_2024, seed_99999)
            u_test_values.append([project_name, p_val_0_vs_2024, p_val_0_vs_99999, p_val_2024_vs_99999])
        with open(key + "/u_test_value.csv", "w") as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(["project", "0 vs 2024", "0 vs 99999", "2024 vs 99999"])
            csv_writer.writerows(u_test_values)

#parser_for_total_time("/home/whx/MutationTesting/Analysis/pitest-logs")
significance_test("/home/whx/MutationTesting/Analysis/pitest-logs")

