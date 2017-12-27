from os import listdir
import matplotlib.pyplot as plt
import pylab
import operator
import numpy as np
import sys
import calendar


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


def identify_the_owner():
    """
    This function returns the full name of owner of the account.
    """
    file = open(sys.argv[1] + "/index.htm")
    profile = file.read()
    file.close()
    result, profile = clear_data("<h1>", "</h1>", profile)
    return result


def count_sent_vs_received_messsages(data, number_of_results):
    """
    This function counts all received and sent messages in every face to face
    conversation.
    """
    final = []
    for conversation in data:
        if len(conversation[0]) == 1:
            final.append([conversation[0], 0, 0, 0])
            for message in conversation[1]:
                final[len(final) - 1][3] += 1
                if message[0] == identify_the_owner():
                    final[len(final) - 1][1] += 1
                else:
                    final[len(final) - 1][2] += 1
    final = sorted(final, key=operator.itemgetter(3))[::-1]

    names = []
    my_messages = []
    others_messages = []
    for i in range(number_of_results):
        names.append(final[i][0][0])
        my_messages.append(final[i][1])
        others_messages.append(final[i][2])
    print(names)
    print(my_messages)
    print(others_messages)
    return names, my_messages, others_messages

def show_sent_vs_received_messages(data, number_of_results):
    """
    This function shows the top results of received and sent messages in
    every face to face conversation in the bar chart.
    """
    result = count_sent_vs_received_messsages(data, number_of_results)
    names = result[0]
    my_messages = result[1]
    others_messages = result[2]

    plt.figure(figsize=(10, 6))
    plt.title("Sent and received messages in the most used conversations")
    plt.bar(
        np.arange(len(my_messages)),
        my_messages,
        width=0.4,
        align='edge',
        alpha=0.7,
        color='r',
        label="Sent messages")
    plt.bar(
        np.arange(len(others_messages)) + 0.4,
        others_messages,
        width=0.4,
        align='edge',
        alpha=0.7,
        color='b',
        label="Received messages")
    plt.legend()
    plt.xticks(np.arange(len(names))+0.4, names, rotation=90)
    plt.ylabel("Number of messages")
    plt.xlim(0, number_of_results)
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

def count_messages_throughout_a_day(data):
    """
    The function counts all sent and received messages messages in every
    minute of a day.
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
    return my_daily_messages, others_daily_messages

def show_messages_throughout_a_day(data):
    """
    The function shows all sent and received messages messages in every
    minute of a day in a plot chart.
    """
    result = count_messages_throughout_a_day(data)
    my_daily_messages = result[0]
    others_daily_messages = result[1]

    plt.figure(figsize=(10, 6))
    plt.title("Sent and received messages throughout a day")
    plt.ylabel("Number of messages")
    plt.plot(
        np.arange(len(my_daily_messages)),
        my_daily_messages,
        color='b',
        alpha=0.7,
        label="Sent messages")
    plt.plot(
        np.arange(len(others_daily_messages)),
        others_daily_messages,
        color='r',
        alpha=0.7,
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
    plt.ylabel("Number of messages")
    plt.xlim(0, 1440)
    plt.tight_layout()
    pylab.savefig("messages_throughout_a_day.png")
    plt.show()

def count_men_vs_women(data):
    """
    This function counts all sent and received messages to men and women
    separately.
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
    return sent_to_men, sent_to_women, received_from_men, received_from_women

def show_men_vs_women(data):
    """
    This function shows all sent and received messages to men and women
    separately in the bar chart.
    """

    result = count_men_vs_women(data)
    sent_to_men = result[0]
    sent_to_women = result[1]
    received_from_men = result[2]
    received_from_women = result[3]

    plt.figure(figsize=(10, 6))
    plt.title("Exchanged messages with men and women")
    plt.bar(np.arange(2), [sent_to_men, sent_to_women],
            color='r', width=0.4, alpha=0.7, label="Sent messages")
    plt.bar(np.arange(2) + 0.40, [received_from_men, received_from_women],
            color='b', width=0.4, alpha=0.7, label="Received messages")
    plt.legend(loc='upper left')
    plt.xticks(np.arange(2)+0.2, ["Men", "Women"])
    plt.ylabel("Number of messages")
    pylab.savefig("men_vs_women.png")
    plt.show()

def count_who_starts_conversation(data, number_of_results):
    """
    This function counts the messages starting conversations sent by me vs.
    those sent by someone else.
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
            for i in range(1, len(conversation[1])):
                message = conversation[1][i]
                time = clear_time(message[1])
                if time[2] != previous_time[2]:
                    if time[3] != previous_time[3] or time[4] != previous_time[4] or (
                            time[2] - previous_time[2]) != 1:
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
    names = []
    me = []
    them = []
    for i in range(number_of_results):
        names.append(final[i][0] + " ")
        me.append(final[i][1])
        them.append(final[i][2])
    return names, me, them

def show_who_starts_conversation(data, number_of_results):
    """
    This function creates the bar chart showing the rates of messages starting
    the conversation compared on basis of who sent that message.
    """
    result = count_who_starts_conversation(data, number_of_results)
    names = result[0]
    me = result[1]
    them = result[2]

    plt.figure(figsize=(10, 6))
    plt.title("Who starts the conversation first")
    plt.bar(
        np.arange(len(me)),
        me,
        width=0.4,
        align="edge",
        alpha=0.7,
        color="r",
        label="Me")
    plt.bar(
        np.arange(len(them)) + 0.4,
        them,
        width=0.4,
        align="edge",
        alpha=0.7,
        color="b",
        label="Other person")
    plt.legend()
    plt.xticks(np.arange(len(names))+0.4, names, rotation=90)
    plt.ylabel("Number of openings")
    plt.xlim(0, number_of_results)
    plt.tight_layout()
    pylab.savefig("who_starts_the_conversation.png")
    plt.show()


def count_msgs_throughout_a_year(data, year):
    """
    This function returns all messages in year by month, separated on messages
    sent by the account owner and received by him.
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
    my_messages = []
    others_messages = []
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
    for month in months:
        if month in months_my_messages:
            my_messages.append(months_my_messages[month])
        else:
            my_messages.append(0)
        if month in months_others_messages:
            others_messages.append(months_others_messages[month])
        else:
            others_messages.append(0)

    return my_messages, others_messages


def show_msgs_throughout_a_year(data):
    """
    This function draws a chart of sent and received messages by month
    throughout several years.
    """
    sent = []
    received = []
    for year in [i + 2014 for i in range(4)]:
        result = count_msgs_throughout_a_year(data, year)
        sent.append(result[0])
        received.append(result[1])

    colors = ["r", "b", "g", "m"]

    plt.figure(figsize=(10, 6))
    plt.title("Sent and received messages by month in last years")

    color_lines = []
    for i in range(4):
        color_lines.append(plt.plot(
            np.arange(12),
            sent[i],
            ls="solid",
            color=colors[i],
            alpha=0.8,
            label=str(2014 + i))[0])
        plt.plot(
            np.arange(12),
            received[i],
            ls="dashed",
            color=colors[i],
            alpha=0.8)

    black_lines = []
    black_lines.append(plt.plot([], [], color="#000000", ls="solid")[0])
    black_lines.append(plt.plot([], [], color="#000000", ls="dashed")[0])

    colors_legend = plt.legend(color_lines,
                               [str(i + 2014) for i in range(4)],
                               loc="upper left")
    plt.legend(black_lines,
               ["Sent messages","Received messages"],
               loc="upper right")
    plt.gca().add_artist(colors_legend)

    plt.xticks(np.arange(13) - 1, calendar.month_name, rotation=70)
    plt.xlim(0, 11)
    plt.ylabel("Number of messages")
    plt.tight_layout()
    pylab.savefig("msgs_throughout_by_month.png")
    plt.show()


show_msgs_throughout_a_year(messages_to_a_list())
show_who_starts_conversation(messages_to_a_list(), 15)
show_men_vs_women(messages_to_a_list())
show_sent_vs_received_messages(messages_to_a_list(), 15)
show_messages_throughout_a_day(messages_to_a_list())