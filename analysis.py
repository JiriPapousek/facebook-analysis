from os import listdir
import matplotlib.pyplot as plt
import pylab
import datetime as dt
from matplotlib.dates import date2num, DateFormatter
import operator
import numpy as np
import sys


"""
This function returns string between first_tag and last_tag in text. It also
returns changed text so that it will not include this string and tags.
"""
def clear_data(first_tag, last_lag, text):
    first_index = text.find(first_tag) + len(first_tag)
    last_index = text.find(last_lag)
    result = text[first_index:last_index]
    text = text[last_index + len(last_lag):len(text)]
    return result, text


"""
This function makes a list of data from the html files of conversations,so
that it would be easier to work with those data later.
"""
def messages_to_a_list():
    chat_names = listdir(sys.argv[1] + "/messages")
    final_list = []

    for chat_name in chat_names:
        file = open(sys.argv[1] + "/messages/" + chat_name)
        conversation = file.read()
        file.close()
        conversation = conversation.split("<div class=\"message\">")
        people_in_conversation, conversation[0] = clear_data(
            "Konverzace s&nbsp;", "</title>", conversation[0])
        people_in_conversation = people_in_conversation.split(",")
        final_list.append([people_in_conversation, []])
        conversation.pop(0)
        for message in conversation:
            """
            Finds a name of user who sent the message, time of sending and
            message itself, afterwards it gets rid of all tags around and
            appends the result as a new value to the list.
            """
            clear_name, message = clear_data(
                "<span class=\"user\">", "</span>", message)
            clear_time, message = clear_data(
                "<span class=\"meta\">", "</span>", message)
            clear_text, message = clear_data("<p>", "</p>", message)
            final_list[len(final_list) -
                       1][1].append([clear_name, clear_time, clear_text])

    return final_list


"""
This function returns the full name of owner of the account.
"""
def identify_the_owner():
    file = open(sys.argv[1] + "/index.htm")
    profile = file.read()
    file.close()
    result, profile = clear_data("<h1>", "</h1>", profile)
    return result


"""
This function counts all received and sent messages in every face to face
conversation. Than it makes a bar chart from these data.
"""
def sent_vs_received_messages(data):
    final = []
    for conversation in data:
        print(conversation)
        if len(conversation[0]) == 1:
            final.append([conversation[0], 0, 0, 0])
            for message in conversation[1]:
                final[len(final) - 1][3] += 1
                if message[0] == identify_the_owner():
                    final[len(final) - 1][1] += 1
                else:
                    final[len(final) - 1][2] += 1
    final = sorted(final, key=operator.itemgetter(3))[::-1]
    print(final)

    my_messages = []
    names = []
    others_messages = []
    for i in range(20):
        print(i)
        names.append(final[i][0][0])
        my_messages.append(final[i][1])
        others_messages.append(final[i][2])
        print(final[i])

    fig = plt.figure()
    ax = fig.add_subplot(111)

    me = ax.bar(
        np.arange(len(names)),
        my_messages,
        width=0.4,
        color='r',
        alpha=0.7)
    other = ax.bar(
        np.arange(len(names)) + 0.4,
        others_messages,
        width=0.4,
        color='b',
        alpha=0.7)
    ax.legend((me[0], other[0]), ('Sent messages', 'Received messages'))

    plt.title("Sent and received messages in the most used conversations")
    plt.xticks(np.arange(len(names)), names, rotation=45)
    ax.autoscale(tight=True)
    plt.tight_layout()
    pylab.savefig("sent_vs_received.png")
    plt.show()


"""
The function returns the list of all messages including certain word written
by specified person.
"""
def count_word(data, word, person):
    word_number = 0
    for conversation in data:
        for message in conversation[1]:
            if word in message[2] and message[0] == person:
                print(str(conversation[0]) + " " +
                      message[1] + " " + message[2])
                word_number += 1
    return word_number


"""
The function counts all sent and received messages messages in every minute of
a day. Than it makes a plot chart from those values.
"""
def messages_throughout_a_day(data):
    my_daily_messages = [0] * 60 * 24
    others_daily_messages = [0] * 60 * 24
    for conversation in data:
        if len(conversation[0]) == 1:
            for message in conversation[1]:
                t = message[1]
                minutes = int(t[t.find(":") + 1:t.find(":") + 3])
                if t[t.find(":") - 2] != " ":
                    hours = int(t[t.find(":") - 2:t.find(":")])
                else:
                    hours = int(t[t.find(":") - 1:t.find(":")])
                time = 60 * hours + minutes

                if message[0] == identify_the_owner():
                    my_daily_messages[time] += 1
                else:
                    others_daily_messages[time] += 1

    plt.title("Sent and received messages throughout a day")
    plt.ylabel("Number of messages")
    plt.plot(
        np.arange(len(my_daily_messages)),
        my_daily_messages,
        '-b',
        label="Sent messages")
    plt.plot(
        np.arange(len(others_daily_messages)),
        others_daily_messages,
        '-r',
        label="Received messages")
    plt.legend(loc='upper left')
    times = ["0:00", "3:00", "6:00", "9:00", "12:00", "15:00", "18:00", "21:00"]
    plt.xticks([180 * i for i in range(8)], times)
    plt.xlim(0, 1440)
    plt.tight_layout()
    pylab.savefig("messages_throughout_a_day.png")
    plt.show()


sent_vs_received_messages(messages_to_a_list())
messages_throughout_a_day(messages_to_a_list())
print(count_word(messages_to_a_list(), "sluníčko", identify_the_owner()))
