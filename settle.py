import pandas as pd
from decimal import *
import imaplib, email, os, base64, warnings

warnings.filterwarnings('ignore')
def get_dataframe():
    csv_file_path = input(
        "Type man to manually input, press enter for automatic email grab, enter file path for prepared csv \n")
    if (csv_file_path == "man"):
        players_dict = {}

        players_dict = get_players_from_input(players_dict)

        players_df = pd.DataFrame.from_dict(players_dict, orient = 'index', columns=[
                                  "name", "net_result"])

        players_df.loc[:, "net_result"] *= 100
        players_df["net_result"] = players_df["net_result"].astype(int)

        print(players_df)
        return players_df
    elif (csv_file_path == ""):
        start_date = input('What is the start date of the pay period? format "yyyy-mm-dd" ex: 2019-06-25\n')
        end_date = input('What is the end date of the pay period? format "yyyy-mm-dd" ex: 2019-06-30\n')

        players_df = get_period_data(start_date, end_date)
        return players_df
    else:
        players_df = get_players_from_csv(csv_file_path)
        return players_df

def get_players_from_raw_csv(file_path, start_date, end_date):
    read_csv = pd.read_csv(file_path, ';')
    if read_csv.DateStarted[0][:10] < start_date or read_csv.DateStarted[0][:10] > end_date: return None
    name_dict = {'#NXAZ3': 'John Lord', '#8CVQF': 'Ben Bae', '#SXRVS': 'Brandon Zheng', '#27W7H': 'Owen Xu',
                 '#KAVY7': 'Mike Vermeer', '#8NNB0': 'Taiyo Hamanaka', '#M28TN': 'Jack Turchetta',
                 '#1S8W8': 'Christopher Shen', '#JU9BW': 'Lenardo Gavaudan',
                 '#RE1D5': 'George Triandafyllides', '#7PMKY': 'Jake Poliner', '#7U4CB': 'Kevin Lu',
                 '#75LHN': 'Justin Bean', '#WPEHN': 'Minjae Kwon', '#0A3X7': 'Issac Aleman',
                 '#EGY05': 'Richard J Li', '#QJ7TP': 'Sam Blumenfeld', '#ESL0T': 'William Wang',
                 '#CJ8XJ': 'Vignesh Valliyur', 
                 '#GWC5V':'Zachary Chivers', '#FV0CJ': 'Richard Zhang',
                 '#N24XP': 'Jaewan Bahk', '#VSVHC': 'Nikolai Mamut',
                 '#9RDUK': 'Patrick Chi', '#AU0T6': 'Raymond Xu'}
    read_csv['name'] = read_csv.ID.map(name_dict)
    read_csv.rename({'Profit': 'net_result', 'Hands': 'hands' }, axis = 'columns', inplace = True)
    cleaned_df = read_csv[["name", "net_result", "hands"]]
    cleaned_df.loc[:, "net_result"] *= 100
    cleaned_df["net_result"] = cleaned_df["net_result"].astype(int)
    cleaned_df["hands"] = cleaned_df["hands"].astype(int)
    cleaned_df = cleaned_df[cleaned_df.net_result != 0]
    cleaned_df = cleaned_df.reset_index()
    cleaned_df = cleaned_df.drop(["index"], axis=1)
    return cleaned_df

def get_players_from_csv(file_path):
    read_csv = pd.read_csv(file_path)
    cleaned_df = read_csv[["name", "net_result"]].dropna(0)
    cleaned_df.loc[:, "net_result"] *= 100
    cleaned_df["net_result"] = cleaned_df["net_result"].astype(int)
    cleaned_df = cleaned_df[cleaned_df.net_result != 0]
    cleaned_df = cleaned_df.reset_index()
    cleaned_df = cleaned_df.drop(["index"], axis=1)
    return cleaned_df

def convert_date(date):
    months = {'01':'Jan', '02':'Feb', '03':'Mar', '04':'Apr', 
     '05':'May', '06':'Jun', '07':'Jul', '08':'Aug',
     '09':'Sep', '10':'Oct', '11':'Nov', '12':'Dec'}
    return date[8:]+'-'+months[date[5:7]]+'-'+date[:4]

def get_raw_csvs(start_date):
    dirName = 'raw_csvs'
    start_date = convert_date(start_date)
    files = []
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")
    email_user = 'degen.c3ntral@gmail.com'
    email_pass = 'D3g3n-c3ntral'
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_user, email_pass)
    mail.select('Inbox')
    type, data = mail.search(None, '(SINCE "'+start_date+'")')
    for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822)' )
        raw_email = data[0][1]
    # converts byte literal to string removing b''
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)
    # downloading attachments
        for part in email_message.walk():
            # this part comes from the snipped I don't understand yet... 
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = part.get_filename()
            if bool(fileName):
                filePath = dirName+'/'+fileName
                if not os.path.isfile(filePath) :
                    fp = open(filePath, 'wb+')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                files.append(filePath)
                subject = str(email_message).split("Subject: ", 1)[1].split("\nTo:", 1)[0]
                print('Downloaded "{file}".'.format(file=fileName))
    return files
    
def get_period_data(start_date, end_date):
    files = get_raw_csvs(start_date)
    data = pd.concat([get_players_from_raw_csv(file, start_date, end_date) for file in files])
    data = data.groupby('name').sum()
    return data

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

    players_dict[name] = [net_result]
    players_dict[name].append(int(input(name + "'s net_result: ")))


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
            gets_extra = players_df.sample(1).index[0]
            players_df.loc[gets_extra, 'net_result'] += -extra_after_split

    else:
        to_edit = input("Who would you like to edit? ")
        if (to_edit == ""):
            return
        else:
            try:
                players_df[to_edit]
            except:
                print(to_edit + " isn't a valid player... Here are the valid players:")
                print(players_df["name"].to_string(index=False))
                return handle_ledger_difference(players_df)

            new_net_value = Decimal(
                input("What should " + to_edit + "'s new net value be? Their current net is "+players_df.loc[to_edit,'net_result']))

            players_df.loc[to_edit, 'net_result'] = int(new_net_value * 100)


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
    max_credit = players_df.loc[max_credit_idx, 'net_result']
    max_debit = players_df.loc[max_debit_idx, 'net_result']

    if (max_credit == 0 and max_debit == 0):
        return

    settle_value = min([-max_debit, max_credit])

    # net_value always stored in index 1 of a row. JOhn changed this, you have name as index so it didnt make sense 
    players_df.loc[max_credit_idx, 'net_result'] -= settle_value
    players_df.loc[max_debit_idx, 'net_result'] += settle_value

    print(max_debit_idx + " pays " +
          str(settle_value / 100) + " to " + max_credit_idx)

    return min_cash_flow(players_df)

def do_rake(players_df):
    if (input('Is there rake or money for coins to be paid? (y/n)')[0] == 'n' ): return players_df
    names = players_df.index.tolist()
    rake_s = pd.Series(data =  [int(input('Enter money for coins/rake to be paid to '+ name + ': '))*100 for name in names], index = names)
    if rake_s.sum() == 0 : return players_df
    players_df['net_result'] -= players_df['hands']/players_df['hands'].sum()*rake_s.sum()
    players_df['net_result'] += rake_s
    players_df['net_result'] = players_df['net_result'].round(0).astype(int)
    return players_df

def main():
    players_df = get_dataframe()
    players_df = do_rake(players_df)
    check_ledger_is_valid(players_df)

    handle_proxies_output = handle_proxies(players_df)
    print(players_df)
    min_cash_flow(players_df)
    print(*handle_proxies_output, sep="\n")

    print("fin")


main()
