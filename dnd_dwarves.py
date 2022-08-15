import math
import random

def roll_dice(size, num=1):
    total = 0
    rolled = 0
    while rolled < num:
        total = total + math.ceil(random.random()*size)
        rolled = rolled + 1
    return(total)

def roll_die(size):
    return(roll_dice(size, 1))


profs = [
    'Miner',
    'Smith',
    'Woodcutter',
    'Farmer',
    'Brewer',
    'Warrior',
    'Crafter'
    ]

deposits = [
    {'name': 'Adamantine', 'depth': 7, 'abundance' : lambda: 1, 'use' : 'Adamantine'},
    {'name': 'Copper', 'depth': 1, 'abundance' : lambda: roll_die(4), 'use' : 'Copper'},
    {'name': 'Gold', 'depth': 5, 'abundance' : lambda: roll_die(3), 'use' : 'Gold'},
    {'name': 'Hematite', 'depth': 2, 'abundance' : lambda: roll_die(3), 'use' : 'Iron'},
    {'name': 'Magnetite', 'depth': 4, 'abundance' : lambda: roll_die(6), 'use' : 'Iron'},
    {'name': 'Silver', 'depth': 3, 'abundance' : lambda: roll_die(3), 'use' : 'Silver'},
    {'name': 'Tin', 'depth': 3, 'abundance' : lambda: roll_die(3), 'use' : 'Tin'},
    ]

ores = [ 'Copper', 'Tin', 'Iron', 'Adamantine', 'Silver', 'Gold']
ore_values = {
    'Copper' : 1,
    'Tin' : 1,
    'Iron' : 3,
    'Silver' : 3,
    'Gold' : 5,
    'Steel' : 5,
    'Adamantine' : 15,
    }

made_values = {
    'Copper' : 5,
    'Tin' : 5,
    'Bronze' : 10,
    'Iron' : 10,
    'Silver' : 10,
    'Gold' : 20,
    'Steel' : 20,
    'Adamantine' : 60,
    }

biomes = [
    { 'name' : 'Tundra', 'trees' : lambda: roll_die(4) - 1, 'threat': lambda: 2 if roll_die(4) == 4 else 0},
    { 'name' : 'Plains', 'trees' : lambda: roll_die(6), 'threat': lambda: 1},
    { 'name' : 'Light Forest', 'trees' : lambda: roll_die(6) + 3, 'threat': lambda: roll_die(2)},
    { 'name' : 'Jungle', 'trees' : lambda: 100, 'threat': lambda: roll_die(4)},
]

def write_log_row(log_row, mode='a'):
    log_string = ','.join([str(e) for e in log_row])+"\n"
    f = open('dwarves_output.csv', mode)
    f.write(log_string)

def setup_logs():
    log_row = ['Full Fort Description', 'Fort Name', 'Biome', 'Coal Level' ]
    for d in deposits:
        if d['name'] != 'Adamantine':
            log_row.append(d['name'] + ' available?')
    log_row.append('Size of Expedition')
    for p in profs:
        log_row.append(p + 's sent')
    log_row.append('Fort Survived?')
    log_row.append('Fort Value')
    write_log_row(log_row, mode='w')

class Fort:
    def __init__(self, biome, deposits, coal_level, dwarves, verbose=False):
        self.verbose = verbose
        self.biome = biome
        self.deposits = deposits
        self.coal_level = coal_level
        self.dwarf_count = {}
        self.total_dwarves = 0
        for prof in profs:
            self.dwarf_count[prof] = 0
        for d in dwarves:
            self.dwarf_count[d] = self.dwarf_count[d] + 1
            self.total_dwarves = self.total_dwarves + 1

        self.setup_empty_hoard()
        self.exterior_access = True
        self.alive = True
        self.age = 0
        self.adamant_thickness = roll_die(20) + 1
        self.gen_name()

    def coal_string(self):
        if self.coal_level == 0:
            return('No Coal')
        elif self.coal_level == 1:
            return('Scarce Coal')
        elif self.coal_level == 2:
            return('Some Coal')
        elif self.coal_level == 3:
            return('Abundant Coal')
        else:
            raise('Coal Level Unexpected')
        
    def gen_name(self):
        prefixes = [ 'Boat', 'Ship', 'Gilded', 'Sorrow', 'Mirror', 'Vault', 'Mountain', 'Ivory', 'Cover', 'Necro', 'Diamond', 'Bolt', 'Tome', 'Relic', 'Release', 'Anvil', 'Handle', 'Sword', 'Mine', 'Gravel', 'Hatchet', 'Shield', 'Clobbered', 'Beaten']
        suffixes = [ 'spires', 'murdered', 'peaks', 'syrup', 'bent', 'girder', 'shoots', 'opens', 'rope', 'caves', 'spear', 'law', 'kiss', 'drinker', 'gleams', 'rings', 'rise', 'spray', 'crimson', 'hammer', 'flares', 'fortunes', 'hollow']
        self.short_name = random.choice(prefixes) + random.choice(suffixes)
        self.full_name = self.short_name + " (" + self.biome['name'] + '; ' + self.coal_string() + '; '
        self.full_name = self.full_name + '; '.join([d['name'] for d in self.deposits if d['name'] != 'Adamantine'])
        self.full_name = self.full_name + ')'
        if self.verbose:
            print(self.full_name)
            
    def setup_empty_hoard(self):
        self.coin = 0
        self.food = self.total_dwarves
        self.wood = 0
        self.coal= 0
        self.hoard = {}
        for o in ores:
            self.hoard[o] = 0

    def get_hoard_amount(self, key):
        return(self.hoard[key])

    def num_prof(self, prof):
        assert( prof in profs )
        count = self.dwarf_count[prof]
        bonus = 0
        if( self.dwarf_count['Brewer'] > 0 ):
            rolled = 0
            while rolled < count:
                rolled = rolled + 1
                if roll_die(10) == 10:
                    bonus = bonus + 1

        if self.verbose:
            print('Fortress has {} {}s ({} + {})'.format(count + bonus, prof, count, bonus))
        return(count + bonus)

    def get_str(self):
        return(self.num_prof('Warrior'))

    def exec_enemy(self):
        threat_level = self.biome['threat']()
        if self.verbose:
            print('Threat is {}\n'.format(threat_level))
        if self.get_str() >= threat_level:
            self.exterior_access = True
        else:
            self.exterior_access = False
        if self.verbose:
            print('Exterior access: {}'.format(self.exterior_access))

    def exec_farm(self):
        num_farm = self.num_prof('Farmer')
        food_per = 10 if self.exterior_access == True else 4
        food_prod = num_farm * food_per
        self.food = self.food + food_prod
        if self.verbose:
            print('Farmers produced {} food ({} each), now have {}\n'.format(food_prod, food_per, self.food))

    def exec_brew(self):
        num_brew = self.num_prof('Brewer')
        food_per = 4
        food_prod = num_brew * food_per
        self.food = self.food + food_prod
        if self.verbose:
            print('Brewers produced {} food ({} each), now have {}\n'.format(food_prod, food_per, self.food))

    def exec_wood(self):
        if(self.exterior_access == True):
            num_woodcutters = self.num_prof('Woodcutter')
            num_trees = self.biome['trees']()
            trees_cut = min(num_woodcutters * 2, num_trees)
            wood_cut = trees_cut
            if self.verbose:
                print('Biome has {} trees, we cut {} for {} wood\n'.format(num_trees, trees_cut, wood_cut))
            self.wood = self.wood + wood_cut

    def exec_mine(self):
        num_miners = self.num_prof('Miner')
        depth_mined = num_miners
        accessible_deposits = [d for d in self.deposits if d['depth'] <= depth_mined]
        for dep in accessible_deposits:
            amount_mined = dep['abundance']()
            self.hoard[dep['use']] = self.hoard[dep['use']] + amount_mined
            if self.verbose:
                print('Mined {} units of {} from {} deposit, now have {}'.format(amount_mined, dep['use'], dep['name'], self.hoard[dep['use']]))
            if dep['name'] == 'Adamantine':
                self.adamant_thickness = self.adamant_thickness - amount_mined
                if self.verbose:
                    print('Adamantine thickness down to {}...'.format(self.adamant_thickness))
                if self.adamant_thickness == 0:
                    self.alive = False
                    if self.verbose:
                        print('DEMONS!')

        coal_chance = 0.1 * self.coal_level
        coal_rolls = 0
        coal_gained = 0
        while(coal_rolls < num_miners):
            if random.random() < coal_chance:
                coal_gained = coal_gained + 1
            coal_rolls = coal_rolls + 1
        self.coal = self.coal + coal_gained
        if self.verbose:
            print('Miners gained {} coal, now {}\n'.format(coal_gained, self.coal))

    def is_fuel_available(self):
        if ( self.wood > 0 or self.coal > 0 or (self.coin >= 3 and self.exterior_access == True)):
            return True
        else:
            return False

    def spend_fuel(self):
        if self.wood > 0:
            self.wood = self.wood - 1
        elif self.coal > 0:
            self.coal = self.coal - 1
        else:
            assert(self.coin >= 3)
            assert(self.exterior_access == True)
            self.coin = self.coin - 3

    def exec_craft(self):
        num_craft = self.num_prof('Crafter')
        while num_craft > 0:
            num_craft = num_craft - 1
            if( self.is_fuel_available() == True and self.hoard['Gold'] >= 1):
                self.spend_fuel()
                self.hoard['Gold'] = self.hoard['Gold'] - 1
                gain_coin = made_values['Gold']
                self.coin = self.coin + gain_coin
                if self.verbose:
                    print('Crafted Gold: now have {} wood, {} coal, {} gold.  +{} coin, now {}\n'.format(self.wood, self.coal, self.hoard['Gold'], gain_coin, self.coin))
            elif( self.is_fuel_available() == True and self.hoard['Silver'] >= 1):
                self.spend_fuel()
                self.hoard['Silver'] = self.hoard['Silver'] - 1
                gain_coin = made_values['Silver']
                self.coin = self.coin + gain_coin
                if self.verbose:
                    print('Crafted Silver: now have {} wood, {} coal, {} silver.  +{} coin, now {}\n'.format(self.wood, self.coal, self.hoard['Silver'], gain_coin, self.coin))
            elif(self.wood > 0 and (self.wood > 5 or self.exterior_access == True)):
                self.wood = self.wood - 1
                profit = 4
                self.coin = self.coin + profit
                if self.verbose:
                    print('Crafted Woodwork: -1 wood, now {}, +{} coin, now {}\n'.format(self.wood, profit, self.coin))
            else:
                if self.verbose:
                    print('Idle Crafter\n')

    def exec_smith(self):
        num_smith = self.num_prof('Smith')
        while num_smith > 0:
            num_smith = num_smith - 1
            if( self.is_fuel_available() == True and self.hoard['Adamantine'] > 0):
                self.spend_fuel()
                self.hoard['Adamantine'] = self.hoard['Adamantine'] - 1
                gain_coin = made_values['Adamantine']
                self.coin = self.coin + gain_coin
                if self.verbose:
                    print('Crafted Adamantine: now have {} wood, {} coal, {} Adamantine.  +{} coin, now {}\n'.format(self.wood, self.coal, self.hoard['Adamantine'], gain_coin, self.coin))
            elif( self.hoard['Iron'] > 0 and self.coal > 2):
                self.coal = self.coal - 2
                self.hoard['Iron'] = self.hoard['Iron'] - 1
                gain_coin = made_values['Steel']
                self.coin = self.coin + gain_coin
                if self.verbose:
                    print('Crafted Steel: now have {} coal, {} iron.  +{} coin, now {}\n'.format(self.coal, self.hoard['Iron'], gain_coin, self.coin))
            elif( self.hoard['Copper'] > 0 and self.hoard['Tin'] > 0 and self.is_fuel_available() == True):
                self.spend_fuel()
                self.hoard['Copper'] = self.hoard['Copper'] - 1
                self.hoard['Tin'] = self.hoard['Tin'] - 1
                gain_coin = made_values['Bronze']
                self.coin = self.coin + gain_coin
                if self.verbose:
                    print('Crafted Bronze: now have {} wood, {} coal, {} copper, {} tin.  +{} coin, now {}\n'.format(self.wood, self.coal, self.hoard['Copper'], self.hoard['Tin'], gain_coin, self.coin))
            elif( self.hoard['Iron'] > 0 and self.is_fuel_available() == True):
                self.spend_fuel()
                self.hoard['Iron'] = self.hoard['Iron'] - 1
                gain_coin = made_values['Iron']
                self.coin = self.coin + gain_coin
                if self.verbose:
                    print('Crafted Iron: now have {} wood, {} coal, {} iron.  +{} coin, now {}\n'.format(self.wood, self.coal, self.hoard['Iron'], gain_coin, self.coin))
            elif( self.hoard['Copper'] > 0 and self.is_fuel_available() == True):
                self.spend_fuel()
                self.hoard['Copper'] = self.hoard['Copper'] - 1
                gain_coin = made_values['Copper']
                self.coin = self.coin + gain_coin
                if self.verbose:
                    print('Crafted Copper: now have {} wood, {} coal, {} copper.  +{} coin, now {}\n'.format(self.wood, self.coal, self.hoard['Copper'], gain_coin, self.coin))
            elif( self.hoard['Tin'] > 0 and self.is_fuel_available() == True):
                self.spend_fuel()
                self.hoard['Tin'] = self.hoard['Tin'] - 1
                gain_coin = made_values['Tin']
                self.coin = self.coin + gain_coin
                if self.verbose:
                    print('Crafted Tin: now have {} wood, {} coal, {} tin.  +{} coin, now {}\n'.format(self.wood, self.coal, self.hoard['Tin'], gain_coin, self.coin))
            else:
                if self.verbose:
                    print('Idle Smith\n')

    def exec_eat(self):
        self.food = self.food - self.total_dwarves
        if self.verbose:
            print('Ate {} food, now {}\n'.format(self.total_dwarves, self.food))

        while ( self.food < 0 and self.exterior_access == True and self.coin >= 3):
            if self.verbose:
                print('Bought food...\n')
            self.coin = self.coin - 3
            self.food = self.food + 1

        if self.food < 0:
            if self.verbose:
                print('Starved to Death!')
            self.alive = False

    def exec_timestep(self):
        assert(self.alive == True)
        self.age = self.age + 1
        if self.verbose:
            print('Executing turn {}\n'.format(self.age))
        self.exec_enemy()
        self.exec_farm()
        self.exec_brew()
        self.exec_wood()
        self.exec_mine()
        self.exec_craft()
        self.exec_smith()
        self.exec_eat()

    def calc_value(self):
        value = self.coin
        if self.verbose:
            print('Final Value: {} coin...'.format(value))
        value = value + (self.food * 0.1)
        if self.verbose:
            print('{} food makes {}...'.format(self.food, value))
        value = value + (self.wood * 0.5)
        if self.verbose:
            print('{} wood makes {}...'.format(self.wood, value))
        value = value + (self.coal)
        if self.verbose:
            print('{} coal makes {}...'.format(self.coal, value))
        for o in ores:
            value = value + (ore_values[o] * self.hoard[o])
            if self.verbose:
                print('{} {} makes {}...'.format(self.hoard[o], o, value))

        return(value)

    def save_log_row(self):
        log_row = [self.full_name, self.short_name, self.biome['name'], self.coal_level]
        for d in deposits:
            if d['name'] != 'Adamantine':
                log_row.append(1 if d in self.deposits else 0)

        log_row.append(self.total_dwarves)
        for p in profs:
            log_row.append(self.dwarf_count[p])
        log_row.append(1 if self.alive == True else 0)
        log_row.append(int(self.calc_value()) if self.alive == True else 0)

        write_log_row(log_row)

def get_random_profs(num_to_send):
    town_square_people = []
    for p in profs:
        num_in_square = 4 + roll_die(20)
        town_square_people = town_square_people + ([p] * int(num_in_square))
    random.shuffle(town_square_people)
    expedition = town_square_people[0:num_to_send]
    return(expedition)
    
def gen_random_fort():
    biome = random.choice(biomes)
    fort_deposits = []
    for d in deposits:
        chance = 0.4 if d['name'] == 'Adamantine' else 0.4
        if random.random() <= chance:
            fort_deposits.append(d)
    
    coal_level = roll_die(4) - 1

    # some restart possibilities
    restart = False
    quality = len([d for d in fort_deposits if d['name'] != 'Adamantine']) + coal_level - (1 if biome['name'] == 'Tundra' else 0)
    if quality < 4:
        return(gen_random_fort())
    num_to_send = 9 + roll_die(4) + roll_die(4)
    expedition = get_random_profs(num_to_send)

    new_fort = Fort(biome, fort_deposits, coal_level, expedition)
    return(new_fort)

def list_teams(num_dwarves, profs_to_consider):
    if num_dwarves == 0:
        return([[]])

    if len(profs_to_consider) == 0:
        return([])
    
    possibilities = []
    num_first_prof = 0
    while num_first_prof <= num_dwarves:
        sub_perms = list_teams(num_dwarves - num_first_prof, profs_to_consider[1:])
        prefix_list = [ profs_to_consider[0] ] * num_first_prof
        possibilities = possibilities + [ prefix_list + p for p in sub_perms ]
        num_first_prof = num_first_prof + 1
    return(possibilities)
    
def summarize_csv():
    f = open('dwarves_output.csv')
    text = f.read()
    text = text.split('\n')
    index_row = text[0]
    cols = index_row.split(',')
    data = []
    row_index = 1
    while row_index < len(text):
        row = text[row_index].split(',')
        if(len(row) < len(cols)):
            break
        row_data = {}
        col_index = 0
        while col_index < len(cols):
            row_data[cols[col_index]] = row[col_index]
            col_index= col_index + 1
        data.append(row_data)
        row_index = row_index + 1

    data = [d for d in data if d['Hematite available?'] == '1' and d['Gold available?'] == '0' and d['Magnetite available?'] == '0']
    
    for p in profs:
        print('Performance by {} count:\n'.format(p))
        num_col = p + 's sent'
        n = 0
        while n < 9:
            count_match = [d for d in data if int(d[num_col]) == n]
            if len( count_match ) > 0:
                sum_val = sum([float(d['Fort Value']) for d in count_match])
                avg_val = sum_val / len(count_match)
                print('Forts with {} {}s average {}$ (sample size of {})'.format(n, p, avg_val, len(count_match)))
            n = n + 1
    return(data)

def main():
    setup_logs()
    count = 1
    num_to_run = 167392
    while count < num_to_run:
        if count%50 == 0:
            print('{}/{}'.format(count, num_to_run))
        site = gen_random_fort()
        while site.alive == True and site.age < 12:
            site.exec_timestep()
        site.save_log_row()
        count = count + 1

def eval_team(team, runs_to_do=100):
    biome = [ b for b in biomes if b['name'] == 'Light Forest'][0]
    fort_deposits_ad = [ d for d in deposits if d['name'] in ['Copper', 'Tin', 'Silver', 'Hematite', 'Adamantine']]
    fort_deposits_no_ad = [ d for d in deposits if d['name'] in ['Copper', 'Tin', 'Silver', 'Hematite']]
    runs = 0
    num_lived = 0
    total_profit = 0
    while runs < runs_to_do:
        site = Fort(biome, fort_deposits_no_ad, 1, team)
        while site.alive == True and site.age < 12:
            site.exec_timestep()
        # no-ad runs are pretty similar so we x10 for speed
        runs = runs + 10
        if site.alive == True:
            num_lived = num_lived + 10
            total_profit = total_profit + (site.calc_value()*10)
    noad_pct_lived = num_lived / runs
    avg_noad_profit = total_profit / runs
    runs = 0
    num_lived = 0
    total_profit = 0
    while runs < runs_to_do:
        site = Fort(biome, fort_deposits_ad, 1, team)
        while site.alive == True and site.age < 12:
            site.exec_timestep()
        runs = runs + 1
        if site.alive == True:
            num_lived = num_lived + 1
            total_profit = total_profit + site.calc_value()
    ad_pct_lived = num_lived / runs
    avg_ad_profit = total_profit / runs
    pct_lived = ( 0.6 * noad_pct_lived ) + ( 0.4 * ad_pct_lived )
    avg_profit = ( 0.6 * avg_noad_profit ) + ( 0.4 * avg_ad_profit )
    info_struct = {'team' : team, 'pct_lived' : pct_lived, 'avg_profit' : avg_profit, 'ad_pct_lived' : ad_pct_lived, 'avg_ad_profit' : avg_ad_profit, 'noad_pct_lived' : noad_pct_lived, 'avg_noad_profit' : avg_noad_profit}
    for prof in profs:
        info_struct['num_'+prof] = len([d for d in team if d == prof])
    return(info_struct)
    
def test_pc_opt():
    possible_teams = list_teams(13, profs)
    scores = []
    i = 1
    for team in possible_teams:
        random.seed('Consistency!')
        if i%100 == 0:
            print('{}/{}'.format(i, len(possible_teams)))
        i = i + 1
        info_struct = eval_team(team)
        scores.append(info_struct)

    return(scores)

random.seed('Boatmurdered')
#main()
#data = summarize_csv()
scores = test_pc_opt()
scores.sort(key = lambda e: e['avg_profit'], reverse=True)

test_count = 0
test_total_surv = 0
test_total_val = 0
while test_count < 10000:
    test_team_orig = get_random_profs(13)
    # reorder for match
    test_team = []
    for prof in profs:
        test_team = test_team + [t for t in test_team_orig if t == prof]
    test_team_scores = [s for s in scores if s['team'] == test_team]
    assert(len(test_team_scores) == 1)
    test_total_surv = test_total_surv + test_team_scores[0]['avg_profit']
    test_total_val = test_total_val + test_team_scores[0]['pct_lived']
    test_count = test_count + 1
king_avg_surv = test_total_surv / test_count
king_avg_val = test_total_val / test_count


