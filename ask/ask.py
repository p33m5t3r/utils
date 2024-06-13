#!/usr/bin/python3

import openai
import sys
import os
import json
import glob
import argparse
import asyncio


# doesn't include the sys prompt, just the user message and context
def fmt_new_message(usr_msg: str, contexts: dict = None) -> dict:
    usr_txt = usr_msg
    if contexts:
        usr_txt += "\n\n context:"
        for k, v in contexts.items():
            usr_txt += f"\n{k}: {v}"

    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": usr_txt
            }
        ]
    }

def fmt_system_prompt(sys_prompt: str) -> dict:
    return {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": sys_prompt
                }
            ]
    }

def fmt_response(resp: str) -> dict:
    return {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": resp
            }
        ]
    }

async def ask_openai(client: openai.OpenAI, messages: list[dict]) -> str:
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    
    response = ""
    try:
        for chunk in stream:
            resp_chunk = chunk.choices[0].delta.content
            if resp_chunk is not None:
                print(resp_chunk, end="")
                response += resp_chunk
        return response

    except asyncio.CancelledError:
        print("<CTRL-C> exiting...")
        return None

def save_convo(buffer_filepath: str, conversation: dict):
    with open(buffer_filepath, 'w') as f:
        json.dump(conversation, f)

def load_convo(buffer_filepath: str) -> dict:
    with open(buffer_filepath, 'r') as f:
        return json.load(f)

async def main():

    SYSTEM_PROMPT = "You are a helpful assistant that provides concise replies to the user's query."

    home_dir = os.environ['HOME']
    BUFFER_FILEPATH = os.path.join(home_dir, ".ask", "buffer.json")

    api_key = os.environ['OPENAI_API_KEY']
    if not api_key:
        return "error: openai API key not found"

    openai.api_key = api_key
    client = openai.OpenAI()

    parser = argparse.ArgumentParser(description="ask an llm a question")
    parser.add_argument('message', type=str, help='message')
    parser.add_argument('-r', '--resume', action='store_true', help='resume conversation')
    parser.add_argument('-t', '--temp', action='store_true', help='dont store convo')
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose')
    parser.add_argument('-c', '--context', nargs='+', help='list of context files')

    args = parser.parse_args()

    # Handle wildcard pattern if provided
    if args.context:
        expanded_files = []
        for file_pattern in args.context:
            expanded_files.extend(glob.glob(file_pattern))
        args.context = expanded_files

    # Print the arguments (or handle them as needed)
    if args.verbose:
        print(f"message: {args.message}")
        print(f"temp flag: {args.temp}")
        print(f"resume flag: {args.resume}")
        print(f"context files: {args.context}")
    
    chat = []
    contexts = {}
    if args.context:
        for context_file in args.context:
            try:
                with open(context_file, 'r') as f:
                    contexts[context_file] = f.read()
            except FileNotFoundError:
                return f"error: context file {context_file} not found..."


    # check for piped input
    if not sys.stdin.isatty():
        piped_input = sys.stdin.read().strip()
        contexts["stdin"] = piped_input
        if args.verbose:
            print(f"piped input: {piped_input}")

    # if we're resuming, load the convo
    if args.resume:
        chat = load_convo(BUFFER_FILEPATH)
    else:
        chat.append(fmt_system_prompt(SYSTEM_PROMPT))
    
    # add the new message to the chat, with relevant contexts
    chat.append(fmt_new_message(args.message, contexts))

    # print the entire chat if verbose arg is set
    if args.verbose:
        print(chat)

    # ask the llm the question, add the response to current chat
    chat.append(fmt_response(await ask_openai(client, chat)))

    # if user asked, save the chat to the buffer
    if not args.temp:
        save_convo(BUFFER_FILEPATH, chat)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("<CTRL-C> exiting...")


