import openai
import json
import argparse

def load_poem(input_file_path):
    '''
    input: str,  input file path(results.json)
    output:list, input+predict
    '''
    with open(input_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    for item in json_data:
        if 'instruction' in item:
            del item['instruction']
    poems = [poem['input']+poem['predict'] for poem in json_data]
    return poems

def score(poems):
    '''
    input:list, poems
    output:(float, float), json file and the avg score of content and format
    '''
    tools = [
    {
        "type": "function",
        "function": {
        # Pick a name for this function
        "name": "auto_grader",
        # Give a description
        "description": "Give a score in the range from 0 to 10 according to the instruction.",
        "parameters": {
            "type": "object",
            "properties": {
            # You can tailor this part to your need.
            "score": {
                "type": "number",
                "description": "Ranging from 0 to 10, the higher the better",
            },
            "reason": {
                "type": "string",
                "description": "A brief explanation of the score",
            }
            },
            "required": ["score", "reason"],
        },
        }
    }
    ]
    score1_list = []
    score2_list = []

    for poem in poems:
        grading_prompt1 = [{"role": "user", "content": "請判斷以下詩句與唐詩格律相似程度，打0到10分的分數，分數越高越相似\n"}]
        grading_prompt2 = [{"role": "user", "content": "請判斷以下唐詩語意通順程度，打0到10分的分數，分數越高越通順\n"}]
        grading_prompt1['content']+=poem
        grading_prompt2['content']+=poem

        tmp1 = []
        tmp2 = []

        for i in range(3):
            completion1 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # You can also try out other models, such as: gpt-4-1106-preview
            messages=grading_prompt1,
            tools=tools,
            temperature=1.0,
            # Force ChatGPT to use our grader function
            tool_choice={"type": "function", "function": {"name": "auto_grader"}}
            )
            completion2 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # You can also try out other models, such as: gpt-4-1106-preview
            messages=grading_prompt2,
            tools=tools,
            temperature=1.0,
            # Force ChatGPT to use our grader function
            tool_choice={"type": "function", "function": {"name": "auto_grader"}}
            )

            tmp1.append(json.loads(completion1.choices[0].message.tool_calls[0].function.arguments))
            tmp2.append(json.loads(completion2.choices[0].message.tool_calls[0].function.arguments))
    
        # cal max score
        max_score1 = 0
        max_score2 = 0
        for score1 in tmp1:
            if score1['score'] > max_score1:
                max_score1 = score1['score']
        for score2 in tmp2:
            if score2['score'] > max_score2:
                max_score2 = score2['score']

        score1_list.append(max_score1)
        score2_list.append(max_score2)

    # cal avg score
    avg_score1, avg_score2 = 0, 0
    for score in score1_list:
        avg_score1+=score
    for score in score2_list:
        avg_score2+=score
    avg_score1/=50
    avg_score2/=50


    return (avg_score1, avg_score2)

if __name__ == "__main__":
    OPENAI_KEY = "sk-xxx"
    openai.api_key = OPENAI_KEY

    poems = load_poem('./results.json')
    score(poems)
    