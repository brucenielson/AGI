# noinspection SpellCheckingInspection
import proplogic.knowledge_base as plkb

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__' or __name__ == 'main':
    print_hi('PyCharm')
    kb = plkb.PLKnowledgeBase()
    input_str: str
    input_str = "A"
    input_str += "\n"
    input_str = input_str + "B"
    input_str = input_str + "\n"
    input_str = input_str + "A AND B => L"
    input_str = input_str + "\n"
    input_str = input_str + "A AND P => L"
    input_str = input_str + "\n"
    input_str = input_str + "B AND L => M"
    input_str = input_str + "\n"
    input_str = input_str + "L AND M => P"
    input_str = input_str + "\n"
    input_str = input_str + "P => Q"
    input_str = input_str + "\n"
    input_str = input_str + "~A => Z"
    input_str = input_str + "\n"
    input_str = input_str + "A and Z => W"
    input_str = input_str + "\n"
    input_str = input_str + "A or Z => ~X"

    kb.add(input_str)
    print(kb.entails('q'))
    print(kb.entails('~q'))


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
