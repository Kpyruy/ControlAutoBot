import time
import sys
import la_bot

def check_remaining_update():
    try:
        while True:
            with open('head/values/remaining_messages.txt', 'r', encoding='utf-8') as file:
                lines = file.readlines()

            if len(lines) >= 1:
                current_remaining_messages = int(lines[0].split("==")[1].strip())

                if current_remaining_messages > 0:
                    decrement_remaining_messages(current_remaining_messages, send_messages)

            with open('head/values/settings.txt', 'r', encoding='cp1251') as file:
                lines = file.readlines()
            send_messages = int(lines[2].split("==")[1].strip())

            if len(lines) >= 3:
                sent_messages = int(lines[2].split("==")[1].strip())
                if sent_messages >= current_remaining_messages:
                    pass

            time.sleep(1)

    except KeyboardInterrupt:
        sys.exit(0)

def decrement_remaining_messages(remaining_messages, send_messages):
    with open('head/values/remaining_messages.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    lines[0] = f"remaining_messages=={remaining_messages}\n"

    new_value = remaining_messages - send_messages

    if new_value > 0:
        with open('head/values/new_message_value.txt', 'w', encoding='utf-8') as file:
            file.write(f"new_value=={new_value}\n")
    else:
        new_value = 0
        autosend = False
        message_auto = None
        message_count = 0

        lines[0] = f"autosend=={autosend}\n"
        with open('head/values/autosend.txt', 'w') as file:
            file.writelines(lines)
        with open('head/values/autosend_data.txt', 'r', encoding='cp1251') as file:
            lines = file.readlines()
        lines[0] = f"message_auto=={message_auto}\n"
        lines[1] = f"message_count=={message_count}\n"
        with open('head/values/autosend_data.txt', 'w', encoding='cp1251') as file:
            file.writelines(lines)

        with open('head/values/new_message_value.txt', 'w', encoding='utf-8') as file:
            file.write(f"new_value=={new_value}\n")

        with open('head/values/residual_message.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        residual_message = lines[0]
        with open('head/values/message.txt', 'w', encoding='utf-8') as file:
            file.write(f"{residual_message}")

check_remaining_update()