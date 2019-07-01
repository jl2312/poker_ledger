import pandas as pd
from decimal import *


def get_dataframe():
    csv_file_path = input(
        "csv file path pls, otherwise hit enter to manually input: ")
    if (csv_file_path == ""):
        players_dict = {}

        players_dict = get_players_from_input(players_dict)

        players_df = pd.DataFrame(data=players_dict.items(), columns=[
                                  "name", "net_result"])

        players_df.loc[:, "net_result"] *= 100
        players_df["net_result"] = players_df["net_result"].astype(int)

        print(players_df)
        return players_df
    else:
        players_df = get_players_from_csv(csv_file_path)
        return players_df


def get_players_from_csv(file_path):
    read_csv = pd.read_csv(file_path)
    cleaned_df = read_csv[["name", "net_result"]].dropna(0)
    cleaned_df.loc[:, "net_result"] *= 100
    cleaned_df["net_result"] = cleaned_df["net_result"].astype(int)
    cleaned_df = cleaned_df[cleaned_df.net_result != 0]
    cleaned_df = cleaned_df.reset_index()
    cleaned_df = cleaned_df.drop(["index"], axis=1)
    return cleaned_df


def get_players_from_input(players_dict):

    name = input("Name please: ")

    if (name == ""):
        return players_dict

    net_result = Decimal(input(name + "'s net_result: "))

    players_dict[name] = net_result

    return get_players_from_input(players_dict)


def check_ledger_is_valid(players_df):
    ledger_sum = players_df["net_result"].sum()
    if (ledger_sum == 0):
        return
    else:
        print("ledger doesn't sum to 0... the difference is " +
              str(-(ledger_sum / 100)))
        handle_ledger_difference(players_df)
        return check_ledger_is_valid(players_df)


def handle_ledger_difference(players_df):
    split_difference = input("split the differnce evenly (y/n)? ")
    if (split_difference == "y"):
        ledger_sum = players_df["net_result"].sum()
        split_difference = - (int(ledger_sum / len(players_df.index)))
        players_df["net_result"] = players_df["net_result"] + split_difference

        extra_after_split = players_df["net_result"].sum()
        if (extra_after_split != 0):
            gets_extra = players_df.sample(len(players_df.index)).iloc[0][0]
            name_idx = int(
                players_df[players_df["name"] == gets_extra].index[0])
            players_df.iat[name_idx, 1] += -extra_after_split

    else:
        to_edit = input("Who would you like to edit? ")
        if (to_edit == ""):
            return
        else:
            try:
                name_idx = int(
                    players_df[players_df["name"] == to_edit].index[0])
            except:
                print(to_edit + " isn't a valid player... Here are the valid players:")
                print(players_df["name"].to_string(index=False))
                return handle_ledger_difference(players_df)

            new_net_value = Decimal(
                input("What should " + to_edit + "'s new net value be? "))

            players_df.iat[name_idx, 1] = int(new_net_value * 100)


def get_getting_proxied_name(players_df):
    getting_proxied = input("Who is getting proxied? ")

    try:
        getting_proxied_idx = int(
            players_df[players_df["name"] == getting_proxied].index[0])

    except:
        print(getting_proxied +
              " isn't a valid player... Here are the valid players:")
        print(players_df["name"].to_string(index=False))
        return get_getting_proxied_name(players_df)

    return getting_proxied_idx


def get_proxy_name(players_df, getting_proxied_idx):
    proxy = input(
        "Who is " + players_df.iloc[getting_proxied_idx][0] + "'s proxy? ")

    try:
        proxy_idx = int(
            players_df[players_df["name"] == proxy].index[0])

    except:
        print(proxy +
              " isn't a valid player... Here are the valid players:")
        print(players_df["name"].to_string(index=False))

    return proxy_idx


def settle_proxies(players_df, getting_proxied_idx, proxy_idx, handle_proxies_output):
    getting_proxied_net_result = players_df.iat[getting_proxied_idx, 1]

    # net_value always stored in index 1 of a row
    players_df.iat[getting_proxied_idx, 1] -= getting_proxied_net_result
    players_df.iat[proxy_idx, 1] += getting_proxied_net_result

    if (getting_proxied_net_result < 0):
        handle_proxies_output.append(players_df.iat[getting_proxied_idx, 0] + " pays " +
                                     str(-getting_proxied_net_result / 100) + " to " + players_df.iat[proxy_idx, 0])
    else:
        handle_proxies_output.append(players_df.iat[proxy_idx, 0] + " pays " +
                                     str(getting_proxied_net_result / 100) + " to " + players_df.iat[getting_proxied_idx, 0])

    return handle_proxies_output


def handle_proxies(players_df):
    done_handling_proxes = False
    handle_proxies_output = []

    while (not done_handling_proxes):
        are_proxies = input("Are there proxies or more proxies? (y/n) ")
        if (are_proxies == "y"):
            getting_proxied_idx = get_getting_proxied_name(players_df)
            proxy_idx = get_proxy_name(players_df, getting_proxied_idx)
            settle_proxies(players_df, getting_proxied_idx,
                           proxy_idx, handle_proxies_output)

        elif (are_proxies == "n"):
            done_handling_proxes = True

        else:
            print("invalid input... please answer (y/n) ")

    return handle_proxies_output


def min_cash_flow(players_df):
    max_credit_idx = players_df["net_result"].idxmax()
    max_debit_idx = players_df["net_result"].idxmin()

    max_credit = players_df.iat[max_credit_idx, 1]
    max_debit = players_df.iat[max_debit_idx, 1]

    if (max_credit == 0 and max_debit == 0):
        return

    settle_value = min([-max_debit, max_credit])

    # net_value always stored in index 1 of a row
    players_df.iat[max_credit_idx, 1] -= settle_value
    players_df.iat[max_debit_idx, 1] += settle_value

    print(players_df.iat[max_debit_idx, 0] + " pays " +
          str(settle_value / 100) + " to " + players_df.iat[max_credit_idx, 0])

    return min_cash_flow(players_df)


def main():
    players_df = get_dataframe()

    check_ledger_is_valid(players_df)

    handle_proxies_output = handle_proxies(players_df)

    min_cash_flow(players_df)
    print(*handle_proxies_output, sep="\n")

    print("fin")


main()
