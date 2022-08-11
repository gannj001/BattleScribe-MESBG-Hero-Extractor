import os
import shutil
import json, json_fix
from bs4 import BeautifulSoup

# IMPORTANT!!!
# Replace <name> with username

# notes:
# get roster name from catalogue node, name attribute

# search dom trees for selectionEntry
# check for child node profiles and profile id
#   from profile id, check for type=hero
#   if type=hero, register name and add hero
# if there is no profile child node, search for entryLinks and entryLink
#   use the name attribute in entryLink
#   check masterRoster for hero with same name
#   if name is found, add the hero



SOURCE_DIR = "C:\\Users\\<name>\\BattleScribe\\data\\Middle-Earth Strategy Battle Game"
TARGET_DIR = os.path.join(os.getcwd(), "data")

class Hero():
    def __init__(self, name="", might=0, fate=0, will=0, wounds=0):
        self.name = name
        self.might = might
        self.will = will
        self.fate = fate
        self.wounds = wounds

    def __json__(self):
        return self.__dict__

class Roster_Crawler():
    def __init__(self, in_file, master_roster=None):
        self.in_file = in_file
        self.master_roster = master_roster

    def read_roster(self):
        with open(self.in_file, encoding='utf-8') as f:
            data = f.read()
            bs_data = BeautifulSoup(data, "xml")
        if not self.master_roster:
            roster = Roster("Master Roster")
        else:
            cat_tag = bs_data.find('catalogue')
            roster = Roster(cat_tag.get("name"))

        hero_tags = bs_data.find_all("profile", {'typeName': 'Hero'})
        for hero_tag in hero_tags:
            h = Hero(name=hero_tag.get("name"))
            print(roster.name, "->", h.name)
            characteristics_tag = hero_tag.find("characteristics")
            try:
                might_tag = characteristics_tag.find("characteristic", {"name": "Might"})
                h.might = might_tag.contents[0]
                will_tag = characteristics_tag.find("characteristic", {"name": "Will"})
                h.will = will_tag.contents[0]
                fate_tag = characteristics_tag.find("characteristic", {"name": "Fate"})
                h.fate = fate_tag.contents[0]
                wounds_tag = characteristics_tag.find("characteristic", {"name": "Wounds"})
                h.wounds = wounds_tag.contents[0]
            except IndexError:
                h.might = 0
                h.will = 0
                h.fate = 0
                h.wounds = 0
            roster.add_hero(h)


        if self.master_roster:
            all_entryLink_tags = bs_data.find_all("entryLink")
            for entryLink_tag in all_entryLink_tags:
                hero_name = entryLink_tag.get("name")
                if hero_name in self.master_roster.heroes.keys():
                    h = self.master_roster.heroes[hero_name]
                    roster.add_hero(h)



        return roster




class Roster():
    def __init__(self, name):
        self.name = name
        self.heroes = {}

    def add_hero(self, hero):
        print(f'Adding {hero.name} to {self.name}')
        self.heroes[hero.name] = hero

    def get_json(self):
        return json.dumps({self.name: self.heroes})

    def __json__(self):
        return self.get_json()

def list_all_files(file_dir=SOURCE_DIR):
    for f_name in os.listdir(file_dir):
        print(f_name)

def unzip_all_files(src_dir=SOURCE_DIR, tgt_dir=TARGET_DIR):
    for f_name in os.listdir(src_dir):
        shutil.unpack_archive(os.path.join(src_dir, f_name), tgt_dir, "zip")

def build_rosters():
    rosters = []
    master_roster_name = "Middle-Earth_Strategy_Battle_Game.gst"
    rc = Roster_Crawler(os.path.join(os.getcwd(), "data", master_roster_name))
    master_roster = rc.read_roster()
    for f_name in os.listdir(os.path.join(os.getcwd(), "data")):
        if f_name != master_roster_name:
            rc = Roster_Crawler(os.path.join(os.getcwd(), "data", f_name), master_roster)
            roster = rc.read_roster()
            rosters.append({"name": roster.name, "heroes": roster.heroes})

    return json.dumps(rosters, indent=4, sort_keys=True)



if __name__ == "__main__":
    unzip_all_files()
    out_json = build_rosters()
    with open("heroes.json", "w") as f:
        f.write(out_json)
