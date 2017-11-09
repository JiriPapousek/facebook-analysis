from os import listdir
import matplotlib.pyplot as plt
import pylab
import operator
import numpy as np
import sys


def clear_data(first_tag, last_lag, text):
    """
    This function returns string between first_tag and last_tag in text. It also
    returns changed text so that it will not include this string and tags.
    """
    first_index = text.find(first_tag) + len(first_tag)
    last_index = text.find(last_lag)
    result = text[first_index:last_index]
    text = text[last_index + len(last_lag):len(text)]
    return result, text


def messages_to_a_list():
    """
    This function makes a list of data from the html files of conversations,so
    that it would be easier to work with those data later.
    """
    chat_names = listdir(sys.argv[1] + "/messages")
    final_list = []

    for chat_name in chat_names:
        file = open(sys.argv[1] + "/messages/" + chat_name)
        conversation = file.read()
        file.close()
        conversation = conversation.split("<div class=\"message\">")
        people_in_conversation, conversation[0] = clear_data(
            "Konverzace s ", "</title>", conversation[0])
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


def identify_the_owner():
    """
    This function returns the full name of owner of the account.
    """
    file = open(sys.argv[1] + "/index.htm")
    profile = file.read()
    file.close()
    result, profile = clear_data("<h1>", "</h1>", profile)
    return result


def sent_vs_received_messages(data, number_of_results):
    """
    This function counts all received and sent messages in every face to face
    conversation. Than it makes a bar chart from these data.
    """
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
    for i in range(number_of_results):
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


def count_word(data, word, person):
    """
    The function returns the list of all messages including certain word written
    by specified person.
    """
    word_number = 0
    for conversation in data:
        for message in conversation[1]:
            if word in message[2] and message[0] == person:
                print(str(conversation[0]) + " " +
                      message[1] + " " + message[2])
                word_number += 1
    return word_number


def clear_time(str):
    """
    Takes plain time string as an argument and converts it to the list of
    separated values.
    """
    minutes = int(str[str.find(":") + 1:str.find(":") + 3])
    if str[str.find(":") - 2] != " ":
        hours = int(str[str.find(":") - 2:str.find(":")])
    else:
        hours = int(str[str.find(":") - 1:str.find(":")])
    day = int(str[0:str.find(".")])
    month = str.split(" ")[1]
    year = int(str.split(" ")[2])
    return [hours, minutes, day, month, year]


def messages_throughout_a_day(data):
    """
    The function counts all sent and received messages messages in every minute of
    a day. Than it makes a plot chart from those values.
    """
    my_daily_messages = [0] * 60 * 24
    others_daily_messages = [0] * 60 * 24
    for conversation in data:
        if len(conversation[0]) == 1:
            for message in conversation[1]:
                t = clear_time(message[1])
                time = 60 * t[0] + t[1]
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
    times = [
        "0:00",
        "3:00",
        "6:00",
        "9:00",
        "12:00",
        "15:00",
        "18:00",
        "21:00"]
    plt.xticks([180 * i for i in range(8)], times)
    plt.xlim(0, 1440)
    plt.tight_layout()
    pylab.savefig("messages_throughout_a_day.png")
    plt.show()


def men_vs_women(data):
    """
    This function counts all sent and received messages to men and women separately
    and than it show results in a bar chart.
    """
    sent_to_women = 0
    sent_to_men = 0
    received_from_women = 0
    received_from_men = 0
    for conversation in data:
        if len(conversation[0]) == 1:
            for message in conversation[1]:
                name = conversation[0][0]
                if message[0] == identify_the_owner():
                    if name[len(name) - 3:len(name)] == "ová":
                        sent_to_women += 1
                    else:
                        sent_to_men += 1
                else:
                    if name[len(name) - 3:len(name)] == "ová":
                        received_from_women += 1
                    else:
                        received_from_men += 1
    plt.title("Exchanged messages with men and women")
    plt.bar(np.arange(2), [sent_to_men, sent_to_women],
            color='r', width=0.4, alpha=0.7, label="Sent messages")
    plt.bar(np.arange(2) + 0.40, [received_from_men, received_from_women],
            color='b', width=0.4, alpha=0.7, label="Received messages")
    plt.legend(loc='upper left')
    plt.xticks(np.arange(2) + 0.4, ["Men", "Women"])
    pylab.savefig("men_vs_women.png")
    plt.show()


def who_starts_conversation(data, number_of_results):
    """
    This function creates the bar chart showing the rates of messages starting
    the conversation and compares them on base of who sent that message.
    """
    final = []
    list_of_greetings = [
        "zdravíčko",
        "ahoj",
        "čau",
        "čus",
        "nazdar",
        "nazdárek",
        "dobrý den"]
    for conversation in data:
        if len(conversation[0]) == 1:
            final.append([conversation[0][0], 0, 0, 0])
            conversation[1] = conversation[1][::-1]
            previous_message = conversation[1][0]
            previous_time = clear_time(previous_message[1])
            previous_time = previous_time[2:len(previous_time)]
            for i in range(1, len(conversation[1])):
                message = conversation[1][i]
                time = clear_time(message[1])
                time = time[2:len(time)]
                if time[0] != previous_time[0]:
                    if time[1] != previous_time[1] or time[2] != previous_time[2] or (
                            time[0] - previous_time[0]) != 1:
                        if message[0] == identify_the_owner():
                            final[len(final) - 1][1] += 1
                        else:
                            final[len(final) - 1][2] += 1
                        final[len(final) - 1][3] += 1
                    else:
                        for greeting in list_of_greetings:
                            if message[2].lower().find(greeting) != -1:
                                if message[0] == identify_the_owner():
                                    final[len(final) - 1][1] += 1
                                else:
                                    final[len(final) - 1][2] += 1
                                final[len(final) - 1][3] += 1
                previous_time = time

    final = sorted(final, key=operator.itemgetter(3))[::-1]
    me = []
    them = []
    names = []
    for i in range(number_of_results):
        me.append(final[i][1])
        them.append(final[i][2])
        names.append(final[i][0])
    plt.title("Who starts the conversation first")
    plt.bar(
        np.arange(
            len(me)),
        me,
        width=0.4,
        alpha=0.7,
        color="r",
        label="Me")
    plt.bar(
        np.arange(
            len(them)) + 0.4,
        them,
        width=0.4,
        alpha=0.7,
        color="b",
        label="Other person")
    plt.legend()
    plt.xticks(np.arange(len(names)), names, rotation=45)
    plt.tight_layout()
    pylab.savefig("who_starts_the_conversation.png")
    plt.show()


def messages_throughout_a_year(data, year):
    """
    This function counts all messages in year by month, than it shows them in
    a plot chart.
    """
    months_my_messages = {}
    months_others_messages = {}
    for conversation in data:
        for message in conversation[1]:
            time = clear_time(message[1])
            if time[4] == year:
                if message[0] == identify_the_owner():
                    if time[3] in months_my_messages:
                        months_my_messages[time[3]] += 1
                    else:
                        months_my_messages[time[3]] = 0
                else:
                    if time[3] in months_others_messages:
                        months_others_messages[time[3]] += 1
                    else:
                        months_others_messages[time[3]] = 0

    months = [
        "leden",
        "únor",
        "březen",
        "duben",
        "květen",
        "červen",
        "červenec",
        "srpen",
        "září",
        "říjen",
        "listopad",
        "prosinec"]

    my_messages = []
    others_messages = []
    for month in months:
        if month in months_my_messages:
            my_messages.append(months_my_messages[month])
        else:
            my_messages.append(0)
        if month in months_others_messages:
            others_messages.append(months_others_messages[month])
        else:
            others_messages.append(0)
    print(my_messages)
    print(others_messages)
    plt.title("Sent and received messages by month in year " + str(year))
    plt.plot(np.arange(12), my_messages, color="r", label="Me")
    plt.plot(np.arange(12), others_messages, color="b", label="Other person")
    plt.xticks(np.arange(12), months, rotation=45)
    plt.legend()
    pylab.savefig("msgs_throughout_" + str(year) + ".png")
    plt.show()


messages_throughout_a_year(messages_to_a_list(), 2010)
who_starts_conversation(messages_to_a_list(), 15)
men_vs_women(messages_to_a_list())
sent_vs_received_messages(messages_to_a_list(), 15)
messages_throughout_a_day(messages_to_a_list())
print(count_word(messages_to_a_list(), ":D", identify_the_owner()))
