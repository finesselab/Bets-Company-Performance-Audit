import pandas as pd
import numpy as np
import pyodbc
from sqlalchemy import create_engine

pd.options.mode.chained_assignment = None

conn2 = pyodbc.connect('Driver={SQL Server};'
                'Server=xxxxxx.cahwy5xxx.useast-1.rds.amazonaws.com,xxxx;'
                                'Database=gamdo;'
                                'uid=xxxxx;pwd=xxxxxxx')
print ("Connected")
cursor = conn2.cursor()


query = '''
          SELECT *
         FROM USERS
        '''

query1 = '''
         SELECT *
        FROM ACTIONS
     '''

query2 = '''
         SELECT *
        FROM BONUS
       '''

users_df = pd.read_sql_query(query, con= conn2)
actions_df = pd.read_sql_query(query1, con= conn2)
bonus_df = pd.read_sql_query(query2, con= conn2)


actions_df_new = actions_df.merge(users_df, how = 'right', left_on = 'USER_ID', right_on = 'User_ID')
actions_df = actions_df_new[['ACTION_TYPE', 'GAME_ID', 'USER_ID', 'AMOUNT', 'DATE', 'USER_TYPE', 'USER_CREATION_DATE']]


actions_df['DATE'] = pd.to_datetime(actions_df['DATE'])

#conditions with ACTION_TYPE and logic

conditions = [
    # Feb: High Roller (Betting volume)
    (actions_df['DATE'].between('2024-02-01', '2024-02-28')) & (actions_df['AMOUNT'] >= 350) & (actions_df['ACTION_TYPE'] == 'bet'),
    
    # Mar: Weekend Special (Deposit incentive)
    (actions_df['DATE'].between('2024-03-01', '2024-03-31')) & (actions_df['AMOUNT'] >= 150) & (actions_df['ACTION_TYPE'] == 'deposit'),
    
    # Apr: Loyalty Reward (Player betting)
    (actions_df['DATE'].between('2024-04-01', '2024-04-30')) & (actions_df['AMOUNT'] >= 350) & (actions_df['USER_TYPE'] == 'player') & (actions_df['ACTION_TYPE'] == 'bet'),
    
    # Jun: Summer Promo (Betting)
    (actions_df['DATE'].between('2024-06-01', '2024-06-30')) & (actions_df['AMOUNT'] >= 250) & (actions_df['ACTION_TYPE'] == 'bet'),
    
    # Aug: VIP Exclusive (High-end Betting)
    (actions_df['DATE'].between('2024-08-01', '2024-08-31')) & (actions_df['AMOUNT'] >= 400) & (actions_df['USER_TYPE'] == 'VIP') & (actions_df['ACTION_TYPE'] == 'bet'),
    
    # Sep: Autumn Bonus (Betting)
    (actions_df['DATE'].between('2024-09-01', '2024-09-30')) & (actions_df['AMOUNT'] >= 200) & (actions_df['ACTION_TYPE'] == 'bet'),
    
    # Nov: Winter Giveaway (Betting)
    (actions_df['DATE'].between('2024-11-01', '2024-11-30')) & (actions_df['AMOUNT'] >= 250) & (actions_df['ACTION_TYPE'] == 'bet'),
    
    # Dec: Holiday Special (Deposit)
    (actions_df['DATE'].between('2024-12-01', '2024-12-30')) & (actions_df['AMOUNT'] >= 100) & (actions_df['ACTION_TYPE'] == 'deposit'),
    
    # Jan 2025: New Year Promo (Deposit)
    (actions_df['DATE'].between('2025-01-01', '2025-01-31')) & (actions_df['AMOUNT'] >= 300) & (actions_df['ACTION_TYPE'] == 'deposit')
]

#Corresponding Bonus Names
bonus_names = [
    'High Roller', 'Weekend Special', 'Loyalty Reward', 'Summer Promo', 
    'VIP Exclusive', 'Autumn Bonus', 'Winter Giveaway', 'Holiday Special', 'New Year Promo'
]

bonus_payouts = [200, 30, 100, 75, 150, 40, 60, 120, 75]

actions_df['BONUS_NAME'] = np.select(conditions, bonus_names, default=None)
actions_df['BONUS_PAYOUT'] = np.select(conditions, bonus_payouts, default=0)


#Welcome Bonus

welcome_mask = (
    (actions_df['USER_CREATION_DATE'].between('2024-01-01', '2024-02-28')) & 
    (actions_df['ACTION_TYPE'] == 'deposit') & (actions_df['AMOUNT'] >= 100)
)
actions_df['WELCOME_BONUS'] = np.where(welcome_mask, 50, 0)



user_welcome_bonus_df = actions_df[['USER_ID', 'WELCOME_BONUS']]
user_welcome_bonus_df.drop_duplicates(subset = ['USER_ID'], inplace = True)


user_welcome_bonus_df = user_welcome_bonus_df.reset_index()
user_welcome_bonus_df.drop(columns = 'index', inplace = True)

#WELCOME BONUS MERGED TO USERS TABLE
users_welcomebonus_df = users_df.merge(user_welcome_bonus_df, how = 'left', left_on = 'User_ID', right_on = 'USER_ID')


users_welcomebonus_df = users_welcomebonus_df[['User_ID', 'USER_TYPE', 'USER_CREATION_DATE', 'WELCOME_BONUS']]

#save users with welcome bonus table to database
engine = create_engine("mssql+pyodbc://", creator=lambda: conn2, fast_executemany=True)
users_welcomebonus_df.to_sql('users_welcomebonus', con=engine, if_exists='append', index=False)


actions_df = actions_df[['ACTION_TYPE', 'GAME_ID', 'USER_ID', 'AMOUNT', 'DATE', 'BONUS_NAME', 'BONUS_PAYOUT']]

#save transactions table to database
actions_df.to_sql('actions_df', con=engine, if_exists='append', index=False)






























