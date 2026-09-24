import os
import shlex


VFS_NAME = "my_vfs"


def parse_command(user_input):
    expanded_input = os.path.expandvars(user_input)

    try:
        parts = shlex.split(expanded_input)
    except ValueError as error:
        print(f"Ошибка разбора команды: {error}")
        return []

    return parts


def command_ls(args):
    print("ls", *args)


def command_cd(args):
    print("cd", *args)


def execute_command(parts):
    if not parts:
        return True

    command = parts[0]
    args = parts[1:]

    if command == "ls":
        command_ls(args)

    elif command == "cd":
        command_cd(args)

    elif command == "exit":
        return False

    else:
        print(f"Ошибка: неизвестная команда '{command}'")

    return True


def main():
    print("Эмулятор оболочки ОС")
    print("Для выхода введите: exit")

    running = True

    while running:
        try:
            user_input = input(f"{VFS_NAME}:~$ ")
            parts = parse_command(user_input)
            running = execute_command(parts)

        except KeyboardInterrupt:
            print("\nДля выхода используйте команду exit.")

        except EOFError:
            print()
            break


if __name__ == "__main__":
    main()