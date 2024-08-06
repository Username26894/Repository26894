import asyncio
import os

import easyocr
import fuzzywuzzy as fw
from fuzzywuzzy import process
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message


TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, folks!")


@dp.message()
async def echo_handler(message: Message) -> None:
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_path = await photo.get_file()
        downloaded_file = await bot.download_file(file_path.file_path)
        result = get_mark(downloaded_file)
        await message.answer(result)
    elif message.text:
        pass
    elif message.photo and message.text:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_path = await photo.get_file()
        downloaded_file = await bot.download_file(file_path.file_path)
        result = get_mark(downloaded_file)
        await message.answer(result)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


def get_mark(downloaded_file):
    reader = easyocr.Reader(['en', 'da', 'es', 'fr', 'pt', 'de', 'cs', 'bs', 'hr', 'rs_latin', 'tr'])
    result = reader.readtext(downloaded_file, detail = 0, low_text=0.1, text_threshold=0.70, rotation_info=[0])

    squad = set()
    res = result.copy()

    for el in result:
        if el.lower().strip() in black_list:
            res.remove(el)
    for el in res:
        if el in all_players:
            squad.add(el)

    for el in result:
        matches = process.extractBests(el, all_players, scorer=lambda x, y: (fw.fuzz.ratio(x, y) + fw.fuzz.token_sort_ratio(x, y)) / 2, score_cutoff=80)
        if el.lower().strip() in black_teams:
            res.remove(el)

    for el in res:
        matches = process.extractBests(el, all_players, scorer=lambda x, y: (fw.fuzz.ratio(x, y) + fw.fuzz.token_sort_ratio(x, y)) / 2, score_cutoff=100)
        if matches:
            squad.add(matches[0][0])


    if len(squad) < 15:
        for i in range(99, 50, -1):
            for el in res:
                matches = fw.process.extractOne(el, all_players, scorer=lambda x, y: (fw.fuzz.ratio(x, y) + fw.fuzz.token_sort_ratio(x, y)) / 2, score_cutoff=i)
                if matches and matches[1] >= i:
                    squad.add(matches[0])
                if len(squad) >= 15:
                    break
            if len(squad) == 15:
                break
  
    return squad


black_list = ['GK', 'MID', 'DEF', 'fwd','bank', 'team', 'aia', 'transfers', 'xpts', 'rteam', 'back', 'pick', 'aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'mar', 'apr', 'may']
black_teams = ['1 DEE', '2 DEE', '3 DEE', '1 MID', '2 MID', '3 MID', '1 FWD', '2 FWD', '3 FWD', 'GKP', 'ars (a)', 'avl (a)', 'bou (a)', 'bre (a)', 'bha (a)', 'che (a)', 'cry (a)', 'eve (a)', 'ful (a)', 'ips (a)', 'lei (a)', 'liv (a)', 'mci (a)', 'mun (a)', 'new (a)', 'nfo (a)', 'sou (a)', 'whu (a)', 'wol (a)', 'ars (h)', 'avl (h)', 'bou (h)', 'bre (h)', 'bha (h)', 'che (h)', 'cry (h)', 'eve (h)', 'ful (h)', 'ips (h)', 'lei (h)', 'liv (h)', 'mci (h)', 'mun (h)', 'new (h)', 'nfo (h)', 'sou (h)', 'whu (h)', 'wol (h)']

all_players = ['Rashford', 'Muniz', 'Longstaff', 'G.Jesus', 'Enzo', 'Wilson', 'Iwobi', 'De Bruyne', 'Pedro Porro', 'Maupay', 'Szoboszlai', 'Alexander-Arnold', 'Rice', 'Kudus', 'Mac Allister', 'Doku', 'Tavernier', 'Lewis-Potter', 'Højlund', 'Mudryk', 'Christie', 'Souček', 'Trippier', 'Gallagher', 'Adingra', 'Kluivert', 'Elliott', 'Toney', 'Edouard', 'Mitoma', 'Diogo J.', 'Almirón', 'Cash', 'Semenyo', 'Neto', 'Beto', 'Werner', 'Antonio', 'Harrison', 'Archer', 'Barkley', 'Brereton Díaz', 'Welbeck', 'J.Ayew', 'McTominay', 'Garner', 'Raúl', 'Robertson', 'Wilson', 'Nørgaard', 'Mario Jr.', 'Awoniyi', 'Barnes', 'De Cordova-Reid', 'Jensen', 'J.Murphy', 'Dunk', 'Janelt', 'Ferguson', 'Sarr', 'Gvardiol', 'Tarkowski', 'Antony', 'Nketiah', 'McAtee', 'Gabriel', 'White', 'Aït-Nouri', 'D.D.Fofana', 'Grealish', 'Casemiro', 'Udogie', 'Hudson-Odoi', 'Romero', 'Madueke', 'Philip', 'Digne', 'Burn', 'Robinson', 'Gusto', 'Lerma', 'Senesi', 'Dalot', 'Haaland', 'Virgil', 'Joelinton', 'Ajer', 'Schär', 'Andersen', 'Disasi', 'Jones', 'Reguilón', 'O.Dango', 'Emerson', 'Mitchell', 'Sinisterra', 'Onana', 'Aké', 'Cairney', 'Walker', 'J.Gomes', 'Konsa', 'Akanji', 'Gilmour', 'Onyeka', 'Buonanotte', 'Ramsey', 'Eriksen', 'Gravenberch', 'Yates', 'Coufal', 'Castagne', 'Cook', 'Rúben', 'Zinchenko', 'Tielemans', 'Estupiñan', 'Schlupp', 'March', 'Bentancur', 'M.Salah', 'Saka', 'Palmer', 'Isak', 'Solanke', 'N.Jackson', 'Watkins', 'Darwin', 'Enes Ünal', 'Brooks', 'Davies', 'Branthwaite', 'Maguire', 'Kovačić', 'Kilman', 'Anderson', 'Bissouma', 'Pinnock', 'Nkunku', 'Danilo', 'Chilwell', 'Enciso', 'N.Semedo', 'Saliba', 'Matheus N.', 'Bobb', 'Mykolenko', 'Collins', 'Muñoz', 'Milner', 'Broja', 'Hinshelwood', 'Dominguez', 'Lallana', 'Caicedo', 'Murillo', 'Tomiyasu', 'Roerslev', 'Kerkez', 'Adama', 'Mee', 'Van Hecke', 'Boly', 'Lo Celso', 'Diego Carlos', 'Miley', 'N.Williams', 'Smith Rowe', 'Toti', 'Toffolo', 'Højbjerg', 'Mainoo', 'Young', 'Duran', 'Álvarez', 'Cucurella', 'Bradley', 'Bellegarde', 'Gomez', 'Alex Moreno', 'Gana', 'Endo', 'Hughes', 'Schade', 'Dawson', 'B.Fernandes', 'Son', 'J.Alvarez', 'Ødegaard', 'Foden', 'Bowen', 'Luis Díaz', 'João Pedro', 'Havertz', 'Gordon', 'Mbeumo', 'Gross', 'Eze', 'Johnson', 'Calvert-Lewin', 'Bailey', 'Gibbs-White', 'Maddison', 'Wood', 'Ward-Prowse', 'Cunha', 'Wissa', 'Mateta', 'Gakpo', 'Diaby', 'Bernardo', 'Martinelli', 'Kulusevski', 'Trossard', 'McNeil', 'Bruno G.', 'Garnacho', 'Richarlison', 'Sterling', 'Sarabia', 'Hee Chan', 'Andreas', 'Elanga', 'A.Doucoure', 'Rodrigo', 'L.Paquetá', 'McGinn', 'Zouma', 'Lukić', 'Yarmoliuk', 'Taylor', 'Fábio Vieira', 'Scott', 'Lewis', 'Jorginho', 'Wharton', 'Colwill', 'N.Aguerd', 'Reed', 'Doherty', 'Vinicius', 'Damsgaard', 'Rogers', 'Zabarnyi', 'Pau', 'James', 'Guéhi', 'Wan-Bissaka', 'Smith', 'Kamara', 'Stones', 'Willock', 'Moder', 'Ings', 'Patterson', 'Aina', 'Tsimikas', 'Kiwior', 'Tete', 'Zanka', 'Doyle', 'Mavropanos', 'Kalajdžić', 'Skipp', 'Lamptey', 'Quansah', 'Fábio Silva', 'Livramento', 'B.Badiashile', 'Konaté', 'Botman', 'Solomon', 'Ward', 'Ream', 'Lindelof', 'Kelly', 'Tosin', 'Tonali', 'Baleba', 'E.Royal', 'Sangaré', 'Hall', 'C.Doucouré', 'Y. Chermiti', 'Thomas', 'Amad', 'H.Bueno', 'Veltman', 'Henry', 'Krafth', 'Van de Ven', 'Maatsen', 'Shaw', 'Aarons', 'Bryan', 'Pellistri', 'Lascelles', 'Webster', 'M.França', 'C.Richards', 'Dahoud', 'Igor', 'Holgate', 'Dendoncker', 'Mount', 'Thomas', 'Coleman', 'Diop', 'Keane', 'Nelson', 'B.Traore', 'Barco', 'Rak-Sakyi', 'Bassey', 'Ahamada', 'Hannibal', 'Deivid', 'Pickford', 'Dobbin', 'Cresswell', 'Veliz', 'Clyne', 'Cornet', 'Chukwuemeka', 'Worrall', 'Fraser', 'Gilchrist', 'Johnson', 'Chalobah', 'Earthy', 'Phillips', 'Evans', 'Hickey', 'Harris', 'Mepham', 'Dasilva', 'Chirewa', 'Faivre', 'H.Traorè', 'Mings', 'Omobamidele', 'Dragusin', 'Clark', 'Flekken', 'Ugochukwu', 'Chiwome', 'Baker-Boaitey', 'Sels', 'Anthony', 'Martinez', 'Casadei', 'Onana', 'Sancho', 'Andrey Santos', 'O’Mahony', 'Nwaneri', 'Foderingham', 'Muric', 'Kellyman', 'Raya', 'Offiah', 'Ederson M.', 'Adams', 'J.Timber', 'Pope', 'S.Bueno', 'Odysseas', 'Neto', 'Ozoh', 'Targett', 'Martinez', 'Kelleher', 'Ramsdale', 'Hill', 'Lavia', 'Henderson', 'Harwood-Bellis', 'Lumley', 'Milenković', 'Amo-Ameyaw', 'Aribo', 'Paulsen', 'Bella-Kotchap', 'Edozie', 'Bednarek', 'Armstrong', 'Bree', 'Lis', 'Larios', 'Alcaraz', 'Ui-jo', 'Bazunu', 'Turner', 'Edwards', 'Kamaldeen', 'Charles', 'Forster', 'Manning', 'Cundle', 'Hause', 'Fabianski', 'Gauci', 'L.Guilherme', 'Buendia', 'Barrenechea', 'Calafiori', 'Irving', 'Tierney', 'Bentley', 'Chiquinho', 'Gonzalez', 'Areola', 'Guedes', 'Hodge', 'Hoever', 'José Sá', 'King', 'Mosquera', 'Pedro Lima', 'Podence', 'R.Gomes', 'Hein', 'Strand Larsen', 'Iling Jr', 'Kesler-Hayden', 'Mara', 'Austin', 'McCarthy', 'Onuachu', 'Smallbone', 'Stephens', 'Stewart', 'Sugawara', 'Walker-Peters', 'Wood', 'Downes', 'Jebbison', 'A.Phillips', 'Bergvall', 'Whiteman', 'Devine', 'Gray', 'Jaden', 'Sousa', 'Sinisalo', 'Olsen', 'Nedeljkovic', 'Scarlett', 'Spence', 'Vicario', 'Marschall', 'Panzo', 'J.Virginia', "O'Brien", 'Morsy', 'Slicker', 'Taylor', 'Tuanzebe', 'Walton', 'Woolfenden', 'Townsend', 'B.Soumaré', 'Cannon', 'Choudhury', 'Coady', 'Daka', 'Chadi Riad', 'Faes', 'Golding', 'Hermansen', 'Iversen', 'Justin', 'Kristiansen', 'Marcal', 'Mavididi', 'McAteer', 'Ndidi', 'Okoli', 'Ricardo', 'Souttar', 'Stolarczyk', 'Vardy', 'Vestergaard', 'Ward', 'Ndaba', 'Luongo', 'A.Fatawu', 'Ladapo', 'Iroegbunam', 'Ndiaye', 'Lindstrøm', "O'Brien", 'Benda', 'Matthews', 'Kamada', 'Leno', 'Johnstone', 'Mbabu', 'Holding', 'Stansfield', 'Ebiowei', 'Sessegnon', 'Al-Hamadi', 'Baggott', 'Broadhead', 'Burgess', 'Burns', 'Chaplin', 'Clarke', 'Davis', 'Delap', 'Edmundson', 'Greaves', 'Harness', 'Hirst', 'Humphreys', 'Hutchinson', 'Winks', 'A.Becker', 'O.Richards', 'Peupion', 'Minteh', 'Malacia', 'Mazilu', 'Zirkzee', 'Yoro', 'A.Murphy', 'Kozlowski', 'I.Osman', 'Fraser', 'Cozier-Duberry', 'Hayden', 'Kuol', 'Lewis', 'Valdimarsson', 'Ruddy', 'Thiago', 'Peart-Harris', 'White', 'Konak', 'Pivas', 'Ji-soo', 'Bowler', 'C.Miguel', 'Da Silva Moreira', 'Dennis', 'Brierley', 'Huijsen', 'Mighten', 'Travers', 'Heaton', 'Sarmiento', 'Bajcetic', 'Steele', 'Carvalho', 'Jørgensen', 'Doak', 'Wiley', 'W.Fofana', 'Sánchez', 'Renato Veiga', 'Petrović', 'Marc Guiu', 'M.Sarr', 'McConnell', 'Morton', 'N.Phillips', 'R.Williams', 'Lukaku', 'Van den Berg', 'Dewsbury-Hall', 'Carson', 'Bettinelli', 'Bergström', 'João Cancelo', 'Arrizabalaga', 'Ângelo', 'Ortega Moreno', 'Wieffer', 'Verbruggen', 'Sávio', 'Undav', 'Bayindir', 'Dúbravka']

if __name__ == "__main__":
    asyncio.run(main())
