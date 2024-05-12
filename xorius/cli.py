import json

import click
import tiktoken
from rich.console import Console
from ullm import LanguageModel


def num_tokens_from_messages(messages):
    """Returns the number of tokens used by a list of messages."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token

    return num_tokens


def select_messages(messages, max_total_tokens=4096, max_output_tokens=1024):
    tokens_num = 0
    selected = []
    for message in messages[::-1]:
        role = message["role"]
        content = (
            message["content"]
            if isinstance(message["content"], str)
            else message["content"][0]["text"]
        )
        cur_token_num = num_tokens_from_messages([{"role": role, "content": content}])
        if tokens_num + cur_token_num + 2 + max_output_tokens > max_total_tokens:
            break

        selected.append(message)
        tokens_num += cur_token_num

    selected = selected[::-1]
    if selected[0]["role"] != "user":  # 确保第一条是用户消息
        selected = selected[1:]

    if not selected:  # 假设 messages 里最后一条是当前用户输入
        selected = [messages[-1]]

    return selected


@click.command()
@click.option("--model-config-file", required=True)
@click.option("--temperature", type=float, default=0.7, show_default=True)
@click.option("--max-tokens", type=int, default=4096, show_default=True)
@click.option("--max-output-tokens", type=int, default=512, show_default=True)
def main(model_config_file, temperature, max_tokens, max_output_tokens):
    console = Console(width=100)
    console.print("[bold green]Xorius[/]: 你好，我是 [bold green]Xorius[/]，你的 AI 助手！\n")

    model_config = json.load(open(model_config_file))
    llm = LanguageModel.from_config(model_config)

    system_message = (
        "You are an AI assistant. Your name is xorius. "
        "You can discuss any ideas and topics with your users, "
        "and you will help your users solve their problems as much as you can."
    )
    max_total_tokens = max_tokens - num_tokens_from_messages(
        [{"role": "system", "content": system_message}]
    )
    memory = []
    while True:
        user_input = console.input("[bold red]You[/]: ").strip()
        if not user_input:
            continue

        memory.append({"role": "user", "content": user_input})

        console.print()
        with console.status("[bold green]Thinking..."):
            messages = select_messages(
                memory, max_total_tokens=max_total_tokens, max_output_tokens=max_output_tokens
            )
            for m in messages:
                print(m)

            answer = llm.chat(
                messages,
                system=system_message,
                config={"temperature": temperature, "max_output_tokens": max_output_tokens},
            )
            console.print(f"[bold green]Xorius[/]: {answer.content}\n")
            memory.append(answer.to_message().model_dump(exclude_none=True))


if __name__ == "__main__":
    main()
