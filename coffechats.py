import sqlite3
import random
import pandas as pd
import numpy as np
import datetime as dt
import gcalcheck as goog
import gcalevent as ct
from dateutil.parser import parse


print('Please enter a monday in the future, following this format: yyyy-m-d')
startDate = raw_input('> ')

con = sqlite3.connect("./coffeechats.sqllite.s3db")
df = pd.read_sql(sql="select * from Person", con=con)

def pairPeople(df):
    # empty
    pairColumns = ['PersonID1', 'Name 1', 'Email 1', 'PersonID2', 'Name 2', 'Email 2']
    dfPairs = pd.DataFrame(columns=pairColumns)

    # Loop until we have paired up everyone based on this number
    unpairedPeople = len(df.index)


    while unpairedPeople > 1:
        print('{0} people left to pair up ...'.format(unpairedPeople))
        isNewPair = False

        while isNewPair == False:

            # Get a random index from 0-num people left
            first = random.randint(0, unpairedPeople - 1)
            second = first

            # Find another person but make sure its not the same as the first person
            while second == first:
                second = random.randint(0, unpairedPeople - 1)

            print('Checking if these people have been paired up before')
            # Lookup Chats table in SQLite db for Person1/Person2

            id1 = df.iloc[[first]]['Id'].values[0]
            dep1 = df.iloc[[first]]['DepartmentID'].values[0]
            name1 = df.iloc[[first]]['Name'].values[0]
            email1 = df.iloc[[first]]['Email'].values[0]

            id2 = df.iloc[[second]]['Id'].values[0]
            dep2 = df.iloc[[second]]['DepartmentID'].values[0]
            name2 = df.iloc[[second]]['Name'].values[0]
            email2 = df.iloc[[second]]['Email'].values[0]

            # different departments
            if dep1 == dep2:
                print('People are in same Department, searching again')
            else:
                # check to see if pair exists in DB
                chat = pd.read_sql_query(sql='SELECT * FROM Chat WHERE PersonId1 = %d AND PersonId2 = %d' % (id1, id2),
                                         con=con)

                if len(chat.index) == 0:
                    print('Pair is new')
                    isNewPair = True

                    print('Paired up Person ID {0} with Person ID {1}'.format(id1, id2))

                    # Create a row with Name1/Email/Name2/Email and append this to our "paired up" list
                    pair = [(id1, name1, email1, id2, name2, email2)]

                    # Convert record ndarray to DataFrame
                    pairDf = pd.DataFrame.from_records(pair, columns=pairColumns)
                    dfPairs = dfPairs.append(pairDf, ignore_index=True)

        # Remove the people from the list of unpaired people
        df = df[df['Name'] != name1]
        df = df[df['Name'] != name2]

        # Remove 2 more people from our list
        unpairedPeople -= 2
        # Eventually df will end up empty

    # Here is our paired up list of people
    dfPairs.to_csv('./paired_people.csv', index=False)
    print(dfPairs)

    # Adding pairs to db. SQLite requires insertions to have an exact header match, so we manipulate df accordingly.
    dfPairs.loc[:, 'ChatTime'] = np.NaN
    dfPairs = dfPairs[['PersonID1', 'PersonID2', 'ChatTime']]
    dfPairs.to_sql("Chat", con, if_exists="append", index=False)
    return dfPairs


def find_appointment(df, date):
    for i in range(0, len(df)):
        row = df.iloc[i]

        name1 = row['Name 1']
        email1 = row['Email 1']
        name2 = row['Name 2']
        email2 = row['Email 2']

        # Get both peoples calendars
        cal1 = goog.get_calendar(email1, date)
        cal2 = goog.get_calendar(email2, date)


        print('email1: %s' % email1)
        print('email2: %s' % email2)
        # This outputs the start and end times for each person's appointments during the week period
        person_1_busy = [{'start': parse(slot['start']), 'end': parse(slot['end'])} for slot in cal1['calendars'][email1]['busy']]
        person_2_busy = [{'start': parse(slot['start']), 'end': parse(slot['end'])} for slot in cal2['calendars'][email2]['busy']]

        #adding a timedelta as defined in nointerns. This defaults to friday 5PM EST of the week entered.
        after, before = goog.compute_end_datetime(date)

        first_available_slot = first_both_available(person_1_busy, person_2_busy, parse(after), parse(before))
        print('First Available Slot: {}'.format(first_available_slot))

        if first_available_slot is not None:
            ct.insert_event(email1, email2, first_available_slot['start'].strftime('%Y-%m-%dT%H:%M:%S%z'), first_available_slot['end'].strftime('%Y-%m-%dT%H:%M:%S%z'))

# this always returns the first slot in the time window, defined by line 99 in no interns
def first_both_available(person_1_busy, person_2_busy, after, before):
    for slot in slots(before, after, end_time_delta=5, step=30):
        if is_available(slot, person_1_busy) \
                and is_available(slot, person_2_busy):
            return slot
        else:
            continue

# Returns whether a given calendar slot is available for a meeting
def is_available(slot, busy):
    for busy_slot in busy:
        if overlap(slot, busy_slot):
            return False
    return True


def overlap(slot1, slot2):
    # assuming slot are datetime, dictionaries
    return ((slot2['start'] <= slot1['start']) and (slot1['start'] <= slot2['end'])) or \
        ((slot1['start'] <= slot2['start']) and (slot2['start'] <= slot1['end']))

# generates slots to check appointment times against
def slots(start, end, end_time_delta, step):
    now = start
    time_slots = []
    while now <= end:
            original = now
            end_hour = now + dt.timedelta(hours=end_time_delta)
            while now < end_hour:
                time_slots.append(now)
                now += dt.timedelta(minutes=step)
            now = original + dt.timedelta(days=1)
    slot_times = []

    for i in range(0, len(time_slots) - 1):
        slot = {'start': time_slots[i], 'end': time_slots[i + 1]}
        slot_times.append(slot)
    return slot_times

pairs = pairPeople(df) 

find_appointment(pairs, startDate)

