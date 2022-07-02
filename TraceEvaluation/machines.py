import numpy as np
import pandas as pd
import pickle
import os.path


def get_all_machine_events(cell):
  return '''SELECT *	FROM 
  `google.com:google-cluster-data`.clusterdata_2019_{}.machine_events ORDER BY time'''.format(cell)


def load_machines(cell, client):
    file = 'machines_{}.pkl'.format(cell)

    if os.path.exists(file):
        print('Cache hit for machine data.')
        return pickle.load( open( file , "rb" ) )
    else:
        print('Cache miss for machine data.')
        data = client.query(get_all_machine_events(cell)).to_dataframe()
        pickle.dump( data, open( file, "wb" ) )
        return data


def down_intervals(machine):
    month = 2678851683489  # 1000000*60*60*24*31
    start = None
    intervals = []
    for idx, trace in enumerate(machine['time']):
        t = machine['event'][idx]
        if t == 2:
            start = trace
        if t in [1, 3] and start:
            interval = (start, trace)
            intervals.append(interval)
            start = None

    if start:
        # If start is still set and not none.
        # then we have no add event at the end
        # hence the interval is still open which we close
        # with the end of month
        interval = (start, month)
        intervals.append(interval)

    return intervals


def availability(machine):
    # a month in micro seconds
    month = 2678851683489  # 1000000*60*60*24*31

    gaps = [0]
    start = None

    for idx, trace in enumerate(machine['time']):
        t = machine['event'][idx]
        if t == 2:
            start = trace
        if t in [1, 3] and start:
            gaps.append(trace - start)
            start = None

    failure_time = sum(gaps)

    return 1 - (failure_time / month)


def get_machine_data(machine_events):
    machines = {}
    platforms = {}
    racks = {}

    for index, row in machine_events.iterrows():

        id = row['machine_id']
        platform = row['platform_id']
        rack = row['switch_id']

        if platform not in platforms:
            platforms[platform] = {
               'machines': [],
               'availability': 1,
            }

        if rack not in racks:
            racks[rack] = []

        if id not in machines:
            machines[id] = {'time': [],
                            'event': [],
                            'availability': 0,
                            'rack': rack,
                            'platform': platform}
            racks[rack].append(id)
            platforms[platform]['machines'].append(id)

        machines[id]['time'].append(row['time'])
        machines[id]['event'].append(row['type'])

        # Check if machines changed swichtes
        assert rack == machines[id]['rack']

    for m in machines:
        # machines[m]['intervals'] = down_intervals(machines[m])
        machines[m]['availability'] = availability(machines[m])

    for p in platforms:
        platforms[p]['availability'] = np.mean([machines[m]['availability'] for m in platforms[p]['machines']])

    return machines, platforms, racks