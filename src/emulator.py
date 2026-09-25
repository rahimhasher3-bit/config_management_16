import argparse
import calendar
import os
import shlex
from datetime import datetime

from vfs import VirtualFileSystem


DEFAULT_VFS_NAME = "my_vfs"


def parse_command(user_input):
    expanded_input = os.path.expandvars(user_input)

    try:
        return shlex.split(expanded_input)
    except ValueError as error:
        print(f"Ошибка разбора команды: {error}")
        return None


def format_prompt(vfs_name, cwd):
    if cwd == "/":
        shown_path = "~"
    else:
        shown_path = cwd

    return f"{vfs_name}:{shown_path}$ "


def command_ls(args, vfs, state):
    if vfs is None:
        print("Ошибка: VFS не загружена")
        return False

    if len(args) > 1:
        print("Ошибка: ls принимает не более одного аргумента")
        return False

    path = args[0] if args else "."

    try:
        items = vfs.list_dir(
            path,
            state["cwd"]
        )

        if items:
            print("  ".join(items))

        return True

    except NotADirectoryError as error:
        print(f"Ошибка: {error}")
        return False


def command_cd(args, vfs, state):
    if vfs is None:
        print("Ошибка: VFS не загружена")
        return False

    if len(args) > 1:
        print("Ошибка: cd принимает не более одного аргумента")
        return False

    path = args[0] if args else "/"

    try:
        state["cwd"] = vfs.change_dir(
            path,
            state["cwd"]
        )
        return True

    except NotADirectoryError as error:
        print(f"Ошибка: {error}")
        return False


def command_date(args):
    if args:
        print("Ошибка: команда date не принимает аргументы")
        return False

    now = datetime.now()

    print(
        now.strftime(
            "%a %b %d %H:%M:%S %Y"
        )
    )

    return True


def command_cal(args):
    now = datetime.now()

    try:
        if len(args) == 0:
            print(
                calendar.month(
                    now.year,
                    now.month
                )
            )

        elif len(args) == 1:
            year = int(args[0])

            print(
                calendar.calendar(year)
            )

        elif len(args) == 2:
            month = int(args[0])
            year = int(args[1])

            if month < 1 or month > 12:
                raise ValueError

            print(
                calendar.month(
                    year,
                    month
                )
            )

        else:
            print(
                "Ошибка: cal принимает "
                "не более двух аргументов"
            )
            return False

    except ValueError:
        print(
            "Ошибка: неверные аргументы команды cal"
        )
        return False

    return True


def execute_command(
    parts,
    vfs=None,
    state=None
):
    if state is None:
        state = {"cwd": "/"}

    if not parts:
        return "continue"

    command = parts[0]
    args = parts[1:]

    if command == "ls":
        if command_ls(args, vfs, state):
            return "continue"
        return "error"

    if command == "cd":
        if command_cd(args, vfs, state):
            return "continue"
        return "error"

    if command == "date":
        if command_date(args):
            return "continue"
        return "error"

    if command == "cal":
        if command_cal(args):
            return "continue"
        return "error"

    if command == "exit":
        return "exit"

    print(
        f"Ошибка: неизвестная команда '{command}'"
    )
    return "error"


def load_vfs(vfs_path):
    if not vfs_path:
        return None

    try:
        vfs = VirtualFileSystem(vfs_path)
        vfs.load()
        return vfs

    except (FileNotFoundError, ValueError) as error:
        print(f"Ошибка загрузки VFS: {error}")
        return None


def show_motd(vfs):
    if vfs is None:
        return

    motd = vfs.get_motd()

    if motd:
        print()
        print("----- MOTD -----")
        print(motd)
        print("----------------")
        print()


def run_startup_script(
    script_path,
    vfs_name,
    vfs,
    state
):
    try:
        with open(
            script_path,
            encoding="utf-8"
        ) as script_file:
            lines = script_file.readlines()

    except OSError as error:
        print(
            f"Ошибка чтения стартового скрипта: "
            f"{error}"
        )
        return "error"

    for line in lines:
        command_line = line.strip()

        if not command_line:
            continue

        print(
            f"{format_prompt(vfs_name, state['cwd'])}"
            f"{command_line}"
        )

        parts = parse_command(command_line)

        if parts is None:
            print("Стартовый скрипт остановлен.")
            return "error"

        result = execute_command(
            parts,
            vfs,
            state
        )

        if result == "error":
            print("Стартовый скрипт остановлен.")
            return "error"

        if result == "exit":
            return "exit"

    return "continue"


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки ОС"
    )

    parser.add_argument(
        "--vfs",
        dest="vfs_path",
        help="Путь к ZIP-архиву VFS"
    )

    parser.add_argument(
        "--script",
        dest="script_path",
        help="Путь к стартовому скрипту"
    )

    return parser.parse_args()


def print_configuration(args):
    print("Параметры запуска:")
    print(
        f"VFS: "
        f"{args.vfs_path or 'не задан'}"
    )

    print(
        f"Стартовый скрипт: "
        f"{args.script_path or 'не задан'}"
    )


def run_repl(
    vfs_name,
    vfs,
    state
):
    print("Эмулятор оболочки ОС")
    print("Для выхода введите: exit")

    while True:
        try:
            user_input = input(
                format_prompt(
                    vfs_name,
                    state["cwd"]
                )
            )

            parts = parse_command(user_input)

            if parts is None:
                continue

            result = execute_command(
                parts,
                vfs,
                state
            )

            if result == "exit":
                break

        except KeyboardInterrupt:
            print(
                "\nДля выхода используйте "
                "команду exit."
            )

        except EOFError:
            print()
            break


def main():
    args = parse_arguments()

    print_configuration(args)

    vfs = load_vfs(args.vfs_path)

    if args.vfs_path and vfs is None:
        return

    if vfs:
        vfs_name = vfs.name
    else:
        vfs_name = DEFAULT_VFS_NAME

    state = {
        "cwd": "/"
    }

    show_motd(vfs)

    if args.script_path:
        result = run_startup_script(
            args.script_path,
            vfs_name,
            vfs,
            state
        )

        if result == "exit":
            return

    run_repl(
        vfs_name,
        vfs,
        state
    )


if __name__ == "__main__":
    main()