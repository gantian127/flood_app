# import requests
#
# url = "http://127.0.0.1:5001/run_model"
# config_file_path = "./flood_model/test_files/config_file.toml"
# dem_file_path = "./flood_model/test_files/geer_canyon.txt"
#
# text_data = {
#     "user_name": "test_request",
# }
#
# response = requests.post(
#     url,
#     data=text_data,
#     files={
#         "dem_file": open(dem_file_path, "rb"),
#         "config_file": open(config_file_path, "rb"),
#     },
# )
#
# if response.status_code == 200:
#     # Save the response content as a zip file
#     with open("./tests/test_request.zip", "wb") as f:
#         f.write(response.content)
#     print("File downloaded successfully.")
# else:
#     print("Error:", response.status_code)
