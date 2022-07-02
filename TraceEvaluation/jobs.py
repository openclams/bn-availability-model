import numpy as np
import pandas as pd
import pickle
import os.path
import time


def make_safe(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()


def get_list_of_services(cell, offset, limit):
  return '''SELECT collection_logical_name as name, user FROM 
  `google.com:google-cluster-data`.clusterdata_2019_{}.collection_events 
  GROUP BY collection_logical_name, user  LIMIT {} OFFSET {}'''.format(cell, limit, offset)


def load_services(cell, client, offset = 0, limit = 100):
    file = 'services_{}_{}_{}.pkl'.format(cell, limit, offset)

    if os.path.exists(file):
        print("Cache hit for service.")
        return pickle.load( open( file , "rb" ) )
    else:
        print("Cache hit for service.")
        data = client.query(get_list_of_services(cell,offset, limit)).to_dataframe()
        pickle.dump( data, open( file, "wb" ) )
        return data

# enum EventType {
#   // The collection or instance was submitted to the scheduler for scheduling.
#   SUBMIT = 0;

#   // The collection or instance was marked not eligible for scheduling by the
#   // batch scheduler.
#   QUEUE = 1;

#   // The collection or instance became eligible for scheduling.
#   ENABLE = 2;

#   // The collection or instance started running.
#   SCHEDULE = 3;

#   // The collection or instance was descheduled because of a higher priority
#   // collection or instance, or because the scheduler overcommitted resources.
#   EVICT = 4;

#   // The collection or instance was descheduled due to a failure.
#   FAIL = 5;

#   // The collection or instance completed normally.
#   FINISH = 6;

#   // The collection or instance was cancelled by the user or because a
#   // depended-upon collection died.
#   KILL = 7;

#   // The collection or instance was presumably terminated, but due to missing
#   // data there is insufficient information to identify when or how.
#   LOST = 8;

#   // The collection or instance was updated (scheduling class or resource
#   // requirements) while it was waiting to be scheduled.
#   UPDATE_PENDING = 9;

#   // The collection or instance was updated while it was scheduled somewhere.
#   UPDATE_RUNNING = 10;
# }

def get_list_of_jobs(service, cell):
    return '''
        SELECT 
            jobs.collection_id as job_id,
            jobs.type as job_event,
            jobs.priority as priority,
            jobs.parent_collection_id as parent,
            tasks.time as time, 
            tasks.instance_index as instance_index, 
            tasks.machine_id as machine_index, 
            tasks.type as task_event
         FROM 
            `google.com:google-cluster-data`.clusterdata_2019_{cell}.collection_events AS jobs
            JOIN `google.com:google-cluster-data`.clusterdata_2019_{cell}.instance_events AS tasks
            ON jobs.collection_id = tasks.collection_id
            WHERE 
            jobs.collection_logical_name="{name}" AND 
            jobs.user="{user}"  AND 
            jobs.type in ( 5, 6 , 7, 8 ) AND
            tasks.type in ( 5, 6, 7, 8 ) 
            ORDER BY tasks.time ASC
    '''.format( cell = cell, name= service['name'], user=service['user'])


def load_jobs(service, cell, client):
    file = 'jobs/jobs_{}_{}_{}.pkl'.format(cell, make_safe(service['name']), make_safe(service['user']))

    if os.path.exists(file):
        print("Cache hit for job.")
        return pickle.load( open( file , "rb" ) )
    else:
        print("Cache miss for jobs.")
        data = client.query(get_list_of_jobs(service, cell)).to_dataframe()
        pickle.dump( data, open( file, "wb" ) )
        return data

def prepare_jobs(jobs, service, cell):

    file = 'jobs/pobs_{}_{}_{}.pkl'.format(cell, make_safe(service['name']), make_safe(service['user']))

    if os.path.exists(file):
        print("Cache hit for prepared jobs.")
        return pickle.load(open(file, "rb"))

    print("Cache miss for prepared jobs.")

    job_data = {}

    start = time.time()
    for jidx, job in jobs.iterrows():

        job_id = int(job['job_id'])
        job_event = job['job_event']
        # parent = int(job['parent'])
        # time = job['time']
        task_id = int(job['instance_index'])
        # machine = int(job['machine_index'])
        # task_event = job['task_event']

        if job_id not in job_data:
            job_data[job_id] = {
                'priority' : int(job['priority']),
                'event' : job_event,
                'tasks' : {}
            }

        job_data[job_id]['tasks'][task_id] = job

    print("Time to prepare the job data: ", time.time() - start)

    pickle.dump(job_data, open(file, "wb"))

    return job_data

# Max prio 450
# free tier < 99 (no SLO)
# beb tier 100 - 115 (no SLO)
# mid tier 116 - 119 (weak SLO)
# prduction tier 120 - 359 (SLO)
# Monitoring Tier > 360

def get_total_jobs(cell, client):

    q = '''SELECT COUNT(DISTINCT collection_id) AS collections FROM
            `google.com:google-cluster-data`.clusterdata_2019_{}.collection_events;'''.format(cell)

    data = client.query(q).to_dataframe()

    return data['collections'][0]

def get_failed_jobs(cell, client):
    q = """SELECT COUNT(DISTINCT collection_id) AS collections FROM
        `google.com:google-cluster-data`.clusterdata_2019_{}.collection_events WHERE type in ( 5,8);""".format(cell)

    data = client.query(q).to_dataframe()

    return data['collections'][0]

def get_total_tasks(cell, client):

    q = '''SELECT COUNT(DISTINCT(CONCAT(collection_id,instance_index))) as instances FROM 
        `google.com:google-cluster-data`.clusterdata_2019_{}.instance_events;'''.format(cell)

    data = client.query(q).to_dataframe()

    return data['instances'][0]

def get_failed_tasks(cell, client):
    q = """SELECT COUNT(DISTINCT(CONCAT(collection_id,instance_index))) as instances FROM 
`google.com:google-cluster-data`.clusterdata_2019_{}.instance_events WHERE type in ( 5,8);""".format(cell)

    data = client.query(q).to_dataframe()

    return data['instances'][0]