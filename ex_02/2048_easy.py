# curses 用来在终端上显示图形界面
import curses
# random 模块用来生成随机数
from random import randrange, choice
# collections 提供了一个字典的子类 defaultdict。可以指定 key 值不存在时，value 的默认值。
from collections import defaultdict

# 【创建棋盘】：初始化棋盘的参数，可以指定棋盘的高和宽以及游戏胜利条件，默认是最经典的 4x4 ～ 2048。
class GameFiled(object):
    # 初始化棋盘参数：
    def __int__(self, width=4, height=4, win=2048):
        self.score = 0 # 当前分数
        self.width = width  # 宽
        self.height = height # 高
        self.win_value = win # 过关分数
        self.high_score = 0 # 最高分
        self.reset() # 游戏重置

    # 游戏中的棋盘操作：随机生成一个2 或 4
    def spaw(self):
        # 从 100 中取一个随机数，如果这个随机数大于 89，new_element 等于 4，否则等于 2
        new_element = 4 if randrange(100) > 89 else 2
        # 得到一个随机空白位置的元组坐标
        (i,j) = choice([
            (i, j) for i in range(self.width) for j in range(self.height)
                if self.field[i][j] == 0
        ])
        # 将随机值复制到空位
        self.field[i][j] = new_element

    # 重置棋盘：在棋盘初始化的时候被调用。它的主要作用是将棋盘所有位置元素复原为 0，然后再在随机位置生成游戏初始的数值
    def reset(self):
        # 更新分数：
        if self.score > self.high_score:
            self.high_score = self.score
        self.score = 0
        # 初始化游戏界面：
        self.field == [[0 for i in range(self.width)] for j in range(self.height)]
        # 在棋盘任意位置生成2个值
        self.spaw()
        self.spaw()

    # 绘制游戏界面：
    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '     (R)Restart (Q)Exit'
        gameover_string = '           GAME OVER'
        win_string = '          YOU WIN!'

        # 绘制函数
        def cast(string):
            # addstr() 方法将传入的内容展示到终端
            screen.addstr(string + '\n')

        # 绘制水平分割线的函数
        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            cast(line)

        # 绘制竖直分割线的函数
        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')

        # 清空屏幕
        screen.clear()
        # 绘制分数和最高分
        cast('SCORE: ' + str(self.score))

        if 0 != self.highscore:
            cast('HIGHSCORE: ' + str(self.highscore))
        # 绘制行列边框分割线
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()
        # 绘制提示文字
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

#【用户行为】:
# ord() 函数以一个字符作为参数，返回参数对应的 ASCII 数值，便于和后面捕捉的键位关联
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
# actions_dict 的输出结果为
# {87: 'Up', 65: 'Left', 83: 'Down', 68: 'Right', 82: 'Restart', 81: 'Exit', 119: 'Up', 97: 'Left', 115: 'Down', 100: 'Right', 114: 'Restart', 113: 'Exit'}
actions_dict = dict(zip(letter_codes, actions * 2))


def get_user_action(keyboard):
    char = "N"
    while char not in actions_dict:
        # 返回按下键位的 ASCII　码值
        char = keyboard.getch()
    # 返回输入键位对应的行为
    return actions_dict[char]

def main(stdscr):
    def init():
        # 重置游戏棋盘
        game_field.reset()
        return 'Game'

    def not_game(state):
        # 根据状态画出游戏的界面
        game_field.draw(stdscr)
        # 读取用户输入得到 action，判断是重启游戏还是结束游戏
        action = get_user_action(stdscr)
        # 如果没有 'Restart' 和 'Exit' 的 action，将一直保持现有状态
        responses = defaultdict(lambda: state)
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        return responses[action]

    def game():
        # 根据状态画出游戏的界面
        game_field.draw(stdscr)
        # 读取用户输入得到 action
        action = get_user_action(stdscr)

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        if game_field.move(action):  # move successful
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'


    state_actions = {
            'Init': init,
            'Win': lambda: not_game('Win'),
            'Gameover': lambda: not_game('Gameover'),
            'Game': game
        }
    # 使用颜色配置默认值
    curses.use_default_colors()

    # 实例化游戏界面对象并设置游戏获胜条件为 2048
    game_field = GameField(win=2048)


    state = 'Init'

    # 状态机开始循环
    while state != 'Exit':
        state = state_actions[state]()


if __name__ == '__main__':
    curses.wrapper(GameFiled())

