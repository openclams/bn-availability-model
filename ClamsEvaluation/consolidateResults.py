import pandas as pd

root_dir = "../"

folder = 'results'

results_file = "out.csv"

counter = 1

frame_labels = []

main_df = pd.DataFrame()

skip = True

for i in range(1, 32):

        data_file = root_dir + "ClamsEvaluation/{}/{}.csv".format(folder,i)

        frame = pd.read_csv(data_file)

        frame['Index'] = counter

        print("Cluster ", i, 'starts at', counter)

        main_df = main_df.append(frame, ignore_index=True)

        counter += 1

print(main_df)
main_df.to_csv(results_file, index=False)