from logic import convert_to_csv

# create test variables
input_folder = 'test/input/arms_oralHistories'
# input_folder = 'test/input/klhs_shino'
output_folder = 'test/test_output'
output_file = 'test_arms_oralHistories.csv'
# output_file = 'test_klhs_shino.csv'
# correct output file (where the manually prepared output is stored)
test_output_file = 'test/output/arms_oralHistories.csv'
# call function
convert_to_csv(input_folder, output_folder, output_file)
