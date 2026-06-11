import pandas as pd
import numpy as np
import pyodbc
from sqlalchemy import create_engine
import json

conn2 = pyodbc.connect('Driver={SQL Server};'
                'Server=xxxxxx.cahwy5xxx.useast-1.rds.amazonaws.com,xxxx;'
                                'Database=gamdo;'
                                'uid=xxxxx;pwd=xxxxxxx')
print ("Connected")
cursor = conn2.cursor()


cc_df = '''
          SELECT *
         FROM customer_cluster
        '''

cc_df = cc_df[['Cluster', 'Recency', 'Frequency', 'Monetary']]
cc_grouped = cc_df.groupby('Cluster').agg({'Recency': np.mean, 'Frequency':np.mean, 'Monetary':np.mean})
cc_grouped = cc_grouped.reset_index()

from groq import Groq

client = Groq()

data_json = cc_grouped.to_json(orient = 'records')

initial_prompt = f"""the following data is a RFM (Recency, Frequency and Monetary Value) cluster averages for customers betting action.
             Recency: Days since the customer's last transaction.
             Frequency: Count of distinct days the customer made a 'BET' transaction,
             Monetary: This represents the total value of bets placed by the user.
             The overall customer (population) averages before segmentation are; Recency: 6.99, Frequency: 25.18, Monetary value: £6722.53
            Summarize the data and make marketing recommendations accordingly {data_json}
            Provide your analysis strictly as a raw JSON object with two separate, flat result sets so I can ingest them into Power BI independently. Do not include any markdown formatting, backticks (```), or introductory text.

Expected JSON Structure:
{{
    "cluster_summaries": [
        {{
            "cluster_id": "Cluster Number/Name",
            "cluster_name": "Descriptive Persona Name",
            "recency_evaluation": "High/Medium/Low compared to population avg, NOTE: The lower the Recency Value, the higher it should be ranked".
            "frequency_evaluation": "High/Medium/Low compared to population avg",
            "monetary_evaluation": "High/Medium/Low compared to population avg",
            "summary_behavior": "Detailed interpretation of this cluster's betting behavior."
        }}
    ],
    "marketing_recommendations": [
        {{
            "cluster_id": "Matching Cluster Number/Name",
            "strategic_objective",
            "recommended_campaign": "Specific marketing action",
            "expected_impact": "What this strategy aims to achieve"
        }}
    ]
}}
"""


# chat_completion = client.chat.completions.create(
messages=[
                {
                    "role": "system",
                    "content": "you are a helpful assistant."
                }
]


messages.append({"role": "user", "content": initial_prompt})

#CONVERSATION LOOP

while True:
    # Send the entire chat history to Groq
    chat_completion = client.chat.completions.create(
        messages=messages,
        model='llama-3.3-70b-versatile',
        response_format={"type": "json_object"}
    )
    
    # Get the model's response
    llm_response = chat_completion.choices[0].message.content
    print("\n--- MODEL RESPONSE ---")
    print(llm_response)
    
    # Append the model's response to the history so it remembers what it said
    messages.append({"role": "assistant", "content": llm_response})
    
    # Ask you if you want to rectify anything
    feedback = input("\nType adjustments/corrections (or type 'SAVE' if it looks perfect): ")
    
    if feedback.strip().upper() == 'SAVE':
        # Parse the final, corrected version
        final_data = json.loads(llm_response)
        break
    else:
        # Append your feedback to the chat history and loop back to regenerate
        messages.append({"role": "user", "content": feedback})



df_summaries = pd.DataFrame(final_data["cluster_summaries"])

#save df_summaries table to database
engine = create_engine("mssql+pyodbc://", creator=lambda: conn2, fast_executemany=True)

df_summaries.to_sql('cluster summaries', con=engine, if_exists='append', index=False)


df_recommendations = pd.DataFrame(final_data["marketing_recommendations"])

df_recommendations.to_sql('cluster recommendations', con=engine, if_exists='append', index=False)
















































