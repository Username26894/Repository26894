import pandas as pd
# need get-response to get the picture from link
import requests
# ocr to search text on screen-shot
import easyocr
# reducing mistakes by reader from easy-ocr
import fuzzywuzzy as fw
from fuzzywuzzy import process
# for telegram-bot
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
# reding df.csv from gc
from google.colab import drive
drive.mount('/content/drive')

# put your perspnal token from bot-father
TOKEN = '****'
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, folks!")


@dp.message()
async def echo_handler(message: Message) -> None:
    if message.photo or (message.photo and message.text):
        file_id = message.photo[-1].file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        image = 'https://api.telegram.org/file/bot' + TOKEN + '/' + file_path
        response = requests.get(image)
        image_data = response.content
        draft = await get_draft(image_data, df)
        result = await get_mark(draft, df, cln)
        user_id = message.from_user.id
        user_name = message.from_user.full_name
        text = f" Hej, {html.bold(message.from_user.full_name)} \n{result}"
        await message.answer(text)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


async def get_draft(img, df):
    '''
    img = link with image from telegram-api
    df = dataframe with all epl-players

    here we use easy-ocr to find all text(players names) on picture
    and find all elements in players-dataframe with fuzzy
    '''
    
    # Reader with all symbols for EPL-players
    reader = easyocr.Reader(['en', 'da', 'es', 'fr', 'pt', 'de', 'cs', 'bs', 'hr', 'rs_latin', 'tr'])
    image = img
    # low_text and text_threshold and rotation_info for search, detail=0 for ignore position data
    result = reader.readtext(image, detail=0, low_text=0.1, text_threshold=0.70, rotation_info=[0])


    squad = list()
    res = result.copy()

    all_players = list(df['web_name'])
    # blacks for extra rows found by reader
    black_list = ['GK', 'MID', 'DEF', 'fwd', 'bank', 'team', 'aia', 'AIA', 'AiA', 'AlA', 'transfers', 'xpts', 'rteam', 'back', 'pick', 'aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'mar', 'apr', 'may', '1 DEE', '2 DEE', '3 DEE', '1 MID', '2 MID', '3 MID', '1 FWD', '2 FWD', '3 FWD', 'GKP']
    black_teams = ['avl (a)', 'bou (a)', 'bre (a)', 'bha (a)', 'che (a)', 'cry (a)', 'eve (a)', 'ful (a)', 'ips (a)',
                   'lei (a)', 'liv (a)', 'mci (a)', 'mun (a)', 'new (a)', 'nfo (a)', 'sou (a)', 'whu (a)', 'wol (a)',
                   'ars (h)', 'avl (h)', 'bou (h)', 'bre (h)', 'bha (h)', 'che (h)', 'cry (h)', 'eve (h)', 'ful (h)',
                   'ips (h)', 'lei (h)', 'liv (h)', 'mci (h)', 'mun (h)', 'new (h)', 'nfo (h)', 'sou (h)', 'whu (h)',
                   'wol (h)', 'ars (a)']


    for el in result:
        if el.lower().strip() in black_list:
            res.remove(el)


    for el in res:
        if el in all_players:
            squad.append(el)
            res.remove(el)
    for el in result:
        if el in black_teams:
            res.remove(el)
    # some rows may found uncorrectly
    for el in res:
        matches = process.extractOne(el, all_players, scorer=lambda x, y: (fw.fuzz.ratio(x, y) + fw.fuzz.token_sort_ratio(x, y)) / 2, score_cutoff=100)
        if matches:
            # some players maybe found twice ('Onana' - Amoudu or Andre)
            duple = ['Lewis', 'White', 'Nelson', 'Ward', 'Martinez', 'Wilson', 'Taylor',
             'King', 'Dennis', 'Neto', 'Johnson', 'Thomas', 'Armstrong', 'Onana',
             'Fraser', "O'Brien", 'Wood']
            if matches[0] not in squad or matches[0] in duple:
                squad.append(matches[0])
    # if we didnt find 15 matches with marks equal 100 
    if len(squad) < 15:
        for i in range(99, 60, -1):
            for el in res:
                matches = fw.process.extractOne(el, all_players, scorer=lambda x, y: (fw.fuzz.ratio(x, y) + fw.fuzz.token_sort_ratio(
                    x, y)) / 2, score_cutoff=i)
                if matches and matches[1] >= i:
                    duple = ['Lewis', 'White', 'Nelson', 'Ward', 'Martinez', 'Wilson', 'Taylor', 'King', 'Dennis', 'Neto', 'Johnson', 'Thomas', 'Armstrong', 'Onana', 'Fraser', "O'Brien", 'Wood']
                    if matches[0] not in squad or matches[0] in duple:
                        squad.append(matches[0])
                if len(squad) >= 15:
                    break
            if len(squad) == 15:
                break
                
    return squad


async def get_mark(squads, df, fixt):
    '''
    get a squad and count his predicted points based on season stats and next opponent
    squads = list with team by screan
    df = dataframe for all players
    fixt = calendar to fixt next opponent
    '''
    duple = ['Lewis', 'White', 'Nelson', 'Ward', 'Martinez', 'Wilson', 'Taylor',
             'King', 'Dennis', 'Neto', 'Johnson', 'Thomas', 'Armstrong', 'Onana',
             'Fraser', "O'Brien", 'Wood']
    
    squad = []
    duplers = []
    # we will ignore some players...
    uncounted = ''
    for el in squads:
        if el in duple:
            duplers.append(el)
        else:
            squad.append(el)

    # short df with founded players
    squad_score = pd.DataFrame(columns=['pts', 'position', 'player', 'sbp'])

    for player in squad:
        pts = 0
        if player in df['web_name'].values:
            pts += await player_pts(player, df, fixt)
            row = df.loc[df['web_name'] == player]
            # print(row)
            # print(type(row))
            new_row = pd.DataFrame({'pts': pts, 'position': row['element_type'].values[0], 'player': player, 'sbp': row['selected_by_percent'].values[0]}, index=[len(squad_score)])
            squad_score = pd.concat([squad_score, new_row])


    if duplers:
        count = {}
        for item in duplers:
            if item in count:
                count[item] += 1
            else:
                count[item] = 1
        duplicates = [item for item, freq in count.items() if freq > 1]
        print(count)
        # if we find both players with duplecated "web_names"
        if duplicates:
            print("duplicates: ", duplicates)
            for el in duplicates:
                # use extra arg with bool-type
                for i in range(2):
                    pts = await player_pts(el, df, fixt, duple=bool(i))
                    rows = df.loc[df['web_name'] == el].reset_index(drop=True)
                    row = rows.iloc[i]
                    new_row = pd.DataFrame({'pts': pts, 'position': row['element_type'], 'player': el, 'sbp': row['selected_by_percent']}, index=[len(squad_score)])
                    # prefer to use squad_score.append, but basic pandas in google-colab supports only pd.concat
                    squad_score = pd.concat([squad_score, new_row])
        if True:
            # if we find only player with duplecated "web_names"
            uncount_players = [item for item, freq in count.items() if freq == 1 and item in duple]
            if len(uncount_players):
                uncounted += ", ".join(uncount_players) + ' out of counting'

    # get some marks for answer
    squad_score = squad_score.sort_values(by='pts', ascending=False)
    expected_points = squad_score.iloc[:11]['pts'].sum()
    ownership = squad_score.iloc[:11]['sbp'].sum()
    df = df.sort_values(by='selected_by_percent', ascending=False)
    most_popular = df.iloc[:11]['selected_by_percent'].sum()
    Template = 'Template: ' + str(round((ownership * 100 / most_popular), 2))
    if len(squad_score) < 5:
        # if your bot in tg-chat he read all pictures, sometimes he should be silent
        # but we need to get more job here(not here) for recognition type of image ("hello, opencv!")
        return 'Nice picture!'
    return f'Expected points: {round(expected_points, 1)} \n{Template}% \n{squad_score.iloc[:11]} \n{uncounted}'




async def player_pts(player, df, fixture, duple=False):
    '''
    this func counts prediction points for player based on his form, position, difference teams strenght

    player = web_name in df
    df = dataframe with all-players
    fixture = dataframe with calendar
    duple = bool cause some web_names may found twice in df
    '''
    
    player_points = 0
    # stars for counting potential bonus points based on player position
    stars = 0
    if duple:
        row = df.loc[df['web_name'] == player].tail(1)
    else:
        row = df.loc[df['web_name'] == player]
    self_team = row['team_name'].values[0]
    vs = fixture.loc[self_team, '4']
    # in fixture-calendar .upper for home games, .lower for away
    if vs == vs.upper():
        enemy = df.loc[df['team_short_name'] == vs].values[0][-2]
        ratio = round(row['team_strength_overall_home'].values[0] / enemy, 2)
    else:
        enemy = df.loc[df['team_short_name'] == vs.upper()].values[0][-1]
        ratio = round(row['team_strength_overall_away'].values[0] / enemy, 2)

    # counting points based on fantasy rules
    if row['element_type'].values[0] == 'DEF' or row['element_type'].values[0] == 'GK':
        if row['element_type'].values[0] == 'DEF':
            stars += 0.25 * row['starts_per_90'].values[0]
        else:
            stars += 0.5 * row['starts_per_90'].values[0]
        player_points += round((float(row['expected_goals_per_90'].values[0]) * 6 + float(
            row['expected_assists_per_90'].values[0]) * 3 + float(row['clean_sheets_per_90'].values[0]) * 4 - float(
            row['expected_goals_conceded_per_90'].values[0]) / 2), 2)
    elif row['element_type'].values[0] == 'MID':
        stars += 0.75 * row['starts_per_90'].values[0]
        player_points += round((float(row['expected_goals_per_90'].values[0]) * 5 + float(
            row['expected_assists_per_90'].values[0]) * 3 + float(row['clean_sheets_per_90'].values[0])), 2)
    elif row['element_type'].values[0] == 'FWD':
        stars += 1.2 * row['starts_per_90'].values[0]
        player_points += round(
            (float(row['expected_goals_per_90'].values[0]) * 4 + float(row['expected_assists_per_90'].values[0]) * 3),
            2)

    summary = round((player_points + stars) * ratio, 2) + row['starts_per_90'].values[0] * 2
    return summary


if __name__ == '__main__':
    # download dataframes with players and calandar
    df = pd.read_csv('/content/drive/MyDrive/latest_df.csv')
    cln = pd.read_json('/content/drive/MyDrive/fixtures.json')
    new_index = pd.Series(['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Ipswich', 'Leicester', 'Liverpool', 'Man City', 'Man Utd', 'Newcastle', "Nott'm Forest", 'Southampton', 'Spurs', 'West Ham', 'Wolves'])
    cln.index = new_index
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)
