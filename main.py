from logic import convert_to_csv

# create test variables
input_folder = 'test/downloader_input'
# input_folder = 'test/input/klhs_shino'
output_folder = 'test/ui_output'
output_file = 'test.csv'
# call function
convert_to_csv(input_folder, output_folder, output_file)
