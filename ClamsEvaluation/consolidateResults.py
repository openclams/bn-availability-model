import pandas as pd

root_dir = "../"

result_folders = {
    "small_multi_final_15" : "Small",
    "large_multi_final_15" : "Large"
}

results_file = "/Users/ottob/Documents/Promotion/disseration/eval/recommendation/results2.csv"

counter = 1

frame_labels = []

main_df = pd.DataFrame()

skip = True

for i in range(1, 32):
    for folder in result_folders:

        data_file = root_dir + "ClamsEvaluation/{}/{}.csv".format(folder,i)

        frame = pd.read_csv(data_file)

        frame['Index'] = counter

        skip = frame['SearchSpaceSize'][0] <= 10000

        if not skip:

            print("Cluster ", i, 'starts at', counter)

            main_df = main_df.append(frame, ignore_index=True)

            frame_labels.append("App "+str(i)+" "+result_folders[folder])
            #frame_labels.append("App" + str(i) +")
            #print(counter,frame)

            counter += 1


    #print("Cluster ", i, 'ends at', counter-1)
    # Jump a count to include the illusion of clustering
    if not skip:
        print("Cluster ", i, 'ends at', counter - 1)
        counter += 1

print(main_df)
main_df.to_csv(results_file, index=False)

settings = {
     "ybar stacked":"",
      "width":"\\linewidth",
      "legend style":{
                     "font":"\\footnotesize","yshift":"-3ex",
                    "legend columns":3,
                     "at":"{(xticklabel cs:0.5)}",
                     "anchor":"north",
                     "draw":"none"},
      "xtick":"data",
      "bar width":"1mm",
      "ymin":0,
      "axis y line*":"none",
      "axis x line*":"none",
      "xticklabels from table":"{\datatable}{name}",
      "x tick label style":{
          "rotate":90,
          "anchor":"east",
          "font":"\\tiny",
          "color":"red"},
      "tick label style":{"font":"\\footnotesize"},
      "label style":{"font":"\\footnotesize"},
      #"xlabel style":"{yshift=-5ex}",
      "xlabel" : "Architectures",
      "ylabel": "{Total Points Explored}",
      "area legend" : ""
}

def serSettings(settings):
    result = ""
    for s in settings:
        if settings[s] == "":
            result += s + ",\n"
        elif isinstance(settings[s], dict):
            result += "\t"+s+"={"+serSettings(settings[s])+"\t},\n"
        else:
            result += "\t"+s+"="+str(settings[s])+",\n"
    return result

labels = "\\pgfplotstableread[col sep=comma]{\nname\n"+"\n".join(frame_labels)+"\n}\\datatable\n\n"


figure = "\\begin{tikzpicture}\n" + labels + \
         "\\begin{axis}["+ \
            serSettings(settings)+ "]\n" + \
        "\\addplot [fill=red,x tick label style={xshift=-0.3cm}] table[x=Index,y=BuildSearchSpaceTime,col sep=comma] {"+results_file+"};\n" + \
        "\\addlegendentry{Load Search Space};\n" + \
        "\\addplot [fill=blue,x tick label style={xshift=-0.3cm}] table[x=Index,y=TotalComputeTime,col sep=comma] {"+results_file+"};\n" + \
        "\\addlegendentry{Harmony Search Execution};\n" + \
         "\\end{axis}\n" + \
         "\\end{tikzpicture}"


print(figure)
f = open("/Users/ottob/Documents/Promotion/disseration/eval/recommendation/figure2.tex", "w")
f.write(figure)
f.close()