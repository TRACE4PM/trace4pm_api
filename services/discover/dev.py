import subprocess

# file = '/home/ania/Desktop/test_app/discovery/test/Digital-Library-logs.csv'
#
# log_file = read_csv(file)
#
# temp_csv_file = '/tmp/temp_log_file.csv'
# log_file.to_csv(temp_csv_file, index=False)
#
# # Construct the command string with the temporary CSV file path as an argument
# command = f"Rscript discover/file.R {temp_csv_file}"

# Execute the command using subprocess

res = subprocess.call("Rscript discover/file.R", shell=True)

res
#
# def test():
#     return "this is a test"
