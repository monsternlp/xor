import click
import openai
import tiktoken
from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from rich.console import Console


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token

        return num_tokens
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not presently implemented for model {model}.\n"
            "See https://github.com/openai/openai-python/blob/main/chatml.md "
            "for information on how messages are converted to tokens."
        )


def select_messages(messages, max_total_tokens=4096, max_output_tokens=1024):
    tokens_num = 0
    selected = []
    for message in messages[::-1]:
        role = "system"
        if isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, HumanMessage):
            role = "user"

        cur_token_num = num_tokens_from_messages([{"role": role, "content": message.content}])
        if tokens_num + cur_token_num + 2 + max_output_tokens > max_total_tokens:
            break

        selected.append(message)
        tokens_num += cur_token_num

    selected = selected[::-1]
    if isinstance(selected[0], AIMessage):  # 确保第一条是用户消息
        selected = selected[1:]

    if not selected:  # 假设 messages 里最后一条是当前用户输入
        selected = message[-1]

    return selected


@click.command()
@click.option("--api-key", required=True)
@click.option("--temperature", type=float, default=0.7, show_default=True)
@click.option("--max-tokens", type=int, default=512, show_default=True)
@click.option("--proxy")
def main(api_key, temperature, max_tokens, proxy):
    console = Console(width=100)
    console.print("[bold green]Xorius[/]: 你好，我是 [bold green]Xorius[/]，你的 AI 助手！\n")

    system_message = SystemMessage(
        content=(
            "You are an AI assistant. Your name is xorius. "
            "You can discuss any ideas and topics with your users, "
            "and you will help your users solve their problems as much as you can."
        ),
    )
    if proxy:
        openai.proxy = proxy

    max_total_tokens = 4096 - num_tokens_from_messages(
        [{"role": "system", "content": system_message.content}]
    )
    llm = ChatOpenAI(temperature=temperature, openai_api_key=api_key, max_tokens=max_tokens)
    memory = ChatMessageHistory()
    while True:
        user_input = console.input("[bold red]You[/]: ").strip()
        if not user_input:
            continue

        memory.add_user_message(user_input)

        console.print()
        with console.status("[bold green]Thinking..."):
            messages = select_messages(
                memory.messages, max_total_tokens=max_total_tokens, max_output_tokens=max_tokens
            )

            answer = llm([system_message] + messages).content.strip()
            console.print(f"[bold green]Xorius[/]: {answer}\n")
            memory.add_ai_message(answer)


if __name__ == "__main__":
    main()
