from Inference.Engine import Engine
import time
import numpy
import re
import subprocess, os


class PrismModelSim(Engine):

    def __init__(self, temp_file_name="cim.sm",
                 prism_location:str = "C:\\Program Files\\prism-4.5\\",
                 prism_bin_path:str = "bin\\prism.bat"):
        Engine.__init__(self, None)
        self.prism_location: str = prism_location
        self.prism_bin_path: str = prism_bin_path
        self.my_env = os.environ.copy()
        self.my_env["PATH"] = self.prism_location + ";"+self.my_env["PATH"]
        self.temp_file_name =temp_file_name
        self.mission_time = 10000
        # -h uses the hybrid engine


    def run(self, solution, *argv):
        args = (
            self.prism_location + self.prism_bin_path,'-javamaxmem', '16g' ,self.temp_file_name , "-pf",
            "R{\"time_unavailable_%s\"}=? [ C<=10 ]" % solution, "-sim")
        start_new_run = time.time()
        try:
            for i in range(self.repetition):
                start = time.time()

                popen = subprocess.Popen(args, env=self.my_env, stdout=subprocess.PIPE)
                # while True:
                #     output = popen.stdout.readline()
                #     if output == '' and popen.poll() is not None:
                #         break
                #     if output:
                #         print(output.strip())
                # exit()
                popen.wait()
                output = str(popen.stdout.read())
                print(output)

                self.availabilityData.append((self.mission_time-float(re.findall(r"Result: ([-+]?\d*\.\d+|\d+)", output)[0]))/self.mission_time)
                self.timeData.append(time.time() - start)

            self.meanAvailability = numpy.mean(self.availabilityData)
            self.meanTime = numpy.mean(self.timeData)
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)
            self.availabilityData = [float('inf')]
            self.meanAvailability = float('inf')
            self.timeData = [float('inf')]
            self.meanTime = float('inf')
            self.is_successful = False