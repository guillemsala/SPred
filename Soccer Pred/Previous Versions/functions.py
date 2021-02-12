
def GenerateDataBase(seasons):
    #df contains all matches from all imported seasons
    df = pd.concat(seasons, axis = 0).reset_index(drop = True)

    #Change Result column to numerical value.
    for index in df.index:
        if df['FTR'][index] == 'D':
            df['FTR'][index] = 1
        elif df['FTR'][index] == 'H':
            df['FTR'][index] = 0
        else:
            df['FTR'][index] = 2

    df['FTR'] = df['FTR'].astype(int)

    #We need the following columns to normalize probability of Win, Draw or Away
    df['B365Tot'] = (1/df['B365H']+1/df['B365D']+1/df['B365A'])
    df['WHTot'] = (1/df['WHH']+1/df['WHD']+1/df['WHA'])

    #Estimate probability of H win, D, or A win.
    df['PH'] = 1/2*(1/df['B365H']*(1/df['B365Tot'])+(1/df['WHH'])*(1/df['WHTot']))
    df['PD'] = 1/2*(1/df['B365D']*(1/df['B365Tot'])+1/df['WHD']*(1/df['WHTot']))
    df['PA'] = 1/2*(1/df['B365A']*(1/df['B365Tot'])+1/df['WHA']*(1/df['WHTot']))

    #Can drop the following columns, as we already have computed probability.
    bet_cols = ['B365H', 'B365D', 'B365A', 'WHH', 'WHD', 'WHA', 'B365Tot', 'WHTot'] #'BWH', 'BWD', 'BWA'
    df.drop(bet_cols, axis = 1, inplace = True)

    #Return df containing 'HomeTeam', 'AwayTeam', 'FTR', 'PH', 'PD', and 'PA'
    return df

def GenerateNewSeason(soup):
    new_season = pd.DataFrame(columns = ['HomeTeam', 'AwayTeam', 'HOdds', 'DOdds', 'AOdds'])

    mydivs = soup.findAll("div", {"class": "ssm-SiteSearchNameMarket gl-Market_General gl-Market_General-topborder gl-Market_General-pwidth50"})
    target_html = []
    for div in mydivs:
        #for subdiv in div.findAll("div", {"class":"ssm-SiteSearchLabelOnlyParticipant gl-Market_General-cn1"}):
        for subdiv in div.findAll("div", {"class":"ssm-SiteSearchLabelOnlyParticipant gl-Market_General-cn1"}):
            for span in subdiv.findAll("span"):
                target_html.append(span)

    new_season['HomeTeam']=[x.text.split(' v ')[0] for x in target_html]
    new_season['AwayTeam']=[x.text.split(' v ')[1] for x in target_html]

    mydivs = soup.findAll("div", {"class": "ssm-SiteSearchOddsOnlyParticipant gl-Participant_General gl-Market_General-cn1"})
    odds = []
    for div in mydivs: 
        for subdiv in div.findAll("div", {"class":"ssm-SiteSearchOddsOnlyParticipant_Wrapper"}):
            for span in subdiv.findAll("span"):
                odds.append(span)


    n = int(len(odds)/3)
    hodds = [float(x.text) for x in odds[0:n]]
    dodds = [float(x.text) for x in odds[n:2*n]]
    aodds = [float(x.text) for x in odds[2*n:3*n]]

    new_season['HOdds'] = hodds
    new_season['DOdds'] = dodds
    new_season['AOdds'] = aodds

    #We need the following columns to normalize probability of Win, Draw or Away
    new_season['OddsTot'] = (1/new_season['HOdds']+1/new_season['DOdds']+1/new_season['AOdds'])

    #Estimate probability of H win, D, or A win.
    new_season['PH'] = 1/new_season['HOdds']*(1/new_season['OddsTot'])
    new_season['PD'] = 1/new_season['DOdds']*(1/new_season['OddsTot'])
    new_season['PA'] = 1/new_season['AOdds']*(1/new_season['OddsTot'])

    #drop unnecessary columns
    new_season.drop('OddsTot', axis = 1, inplace = True)

    return new_season

def cleanna(df):
    df.dropna(axis = 0, inplace = True)

def DropNotInTeams(new_season, df):
    new_season = new_season[(new_season['HomeTeam'].isin(df['HomeTeam'].unique())) & (new_season['AwayTeam'].isin(df['HomeTeam'].unique()))]
    return new_season
