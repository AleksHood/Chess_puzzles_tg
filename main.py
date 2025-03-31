from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.error import NetworkError
from PIL import Image, ImageDraw, ImageFont
import random
import os
import asyncio


# --- Скрипт преобразования задач из файла ---
def is_valid_fen(fen):
    return "/" in fen and " " in fen


def is_solution_line(line):
    return "#" in line


def parse_chess_problems(file_path):
    problems = {
        "Мат в 1 ход": [],
        "Мат в 2 хода": [],
        "Мат в 3 хода": [],
        "Мат в 4 хода": []
    }

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines if line.strip()]

    i = 0
    while i < len(lines):
        fen = lines[i]

        if not is_valid_fen(fen):
            i += 1
            continue

        # Проверяем следующую строку (если она есть)
        solution = None
        if i + 1 < len(lines) and is_solution_line(lines[i + 1]):
            solution = lines[i + 1]

        if solution:
            # Если есть решение, определяем количество ходов
            moves = solution.split()
            mate_in = 0
            for j, move in enumerate(moves):
                if '#' in move:
                    mate_in = sum(1 for m in moves[:j + 1] if '.' in m or '...' in m)
                    break
            if mate_in == 0:
                mate_in = 1
            i += 2  # Пропускаем FEN и решение
        else:
            # Если решения нет, считаем "Мат в 1 ход"
            mate_in = 1
            i += 1  # Пропускаем только FEN

        task = {
            "fen": fen,
            "solution": solution if solution else "Нет решения в файле"
        }

        if mate_in == 1:
            problems["Мат в 1 ход"].append(task)
        elif mate_in == 2:
            problems["Мат в 2 хода"].append(task)
        elif mate_in == 3:
            problems["Мат в 3 хода"].append(task)
        elif mate_in == 4:
            problems["Мат в 4 хода"].append(task)

    return problems


def generate_python_code(problems):
    code = "tasks = {\n"
    for category, task_list in problems.items():
        code += f'    "{category}": [\n'
        for task in task_list:
            code += "        {\n"
            code += f'            "fen": "{task["fen"]}",\n'
            code += f'            "solution": "{task["solution"]}"\n'
            code += "        },\n"
        code += "    ],\n"
    code += "}"
    return code


file_path = r"C:\Users\FuckFaceOfNorth\PycharmProjects\TANDD\chess_problems.txt"

try:
    problems = parse_chess_problems(file_path)
    python_code = generate_python_code(problems)
    with open("tasks_output.py", "w", encoding='utf-8') as output_file:
        output_file.write(python_code)
except FileNotFoundError:
    print(f"Файл {file_path} не найден. Используется стандартный набор задач.")
    tasks = {
        "Мат в 1 ход": [
            {"fen": "8/8/8/8/8/8/6Qk/6K1 w - - 0 1", "solution": "1. Qg4#"},
            {"fen": "8/8/4np2/4k3/4P3/4K3/8/3R4 w - - 0 1", "solution": "Нет решения в файле"},
        ],
        "Мат в 2 хода": [
            {"fen": "r2qkb1r/pp2nppp/3p4/2pNN1B1/2BnP3/3P4/PPP2PPP/R2bK2R w KQkq - 1 0",
             "solution": "1. Кf6+ gxf6 2. Сxf7#"},
            {"fen": "7k/1p4p1/p4b1p/3N3P/2p5/2rb4/PP2r3/K2R2R1 b - - 0 1", "solution": "1... Rc1+ 2. Rxc1 Bxb2#"},
        ],
        "Мат в 3 хода": [
            {"fen": "8/8/8/5K2/8/6Q1/6pk/8 w - - 0 1", "solution": "1. Qf3 Ka4 2. Qb3+ Ka5 3. Qb5#"},
            {"fen": "8/8/8/8/5Q2/6p1/6pk/6K1 w - - 0 1", "solution": "1. Qf5 g2 2. Qe4 g1=Q 3. Qb7#"},
        ],
        "Мат в 4 хода": [
            {"fen": "8/8/8/8/8/5Q2/6pk/5K2 w - - 0 1", "solution": "1. Qf5 g5 2. Qe4 g4 3. Qd3 g3 4. Qb5#"},
            {"fen": "8/8/8/8/5K2/6Q1/6p1/6k1 w - - 0 1", "solution": "1. Qf2 g5 2. Qe3 g4 3. Qd2 g3 4. Qf2#"},
        ]
    }
else:
    try:
        exec(python_code)
    except SyntaxError as e:
        print(f"Ошибка в сгенерированном коде: {e}. Используется стандартный набор задач.")
        tasks = {
            "Мат в 1 ход": [
                {"fen": "8/8/8/8/8/8/6Qk/6K1 w - - 0 1", "solution": "1. Qg4#"},
                {"fen": "8/8/4np2/4k3/4P3/4K3/8/3R4 w - - 0 1", "solution": "Нет решения в файле"},
            ],
            "Мат в 2 хода": [
                {"fen": "r2qkb1r/pp2nppp/3p4/2pNN1B1/2BnP3/3P4/PPP2PPP/R2bK2R w KQkq - 1 0",
                 "solution": "1. Кf6+ gxf6 2. Сxf7#"},
                {"fen": "7k/1p4p1/p4b1p/3N3P/2p5/2rb4/PP2r3/K2R2R1 b - - 0 1", "solution": "1... Rc1+ 2. Rxc1 Bxb2#"},
            ],
            "Мат в 3 хода": [
                {"fen": "8/8/8/5K2/8/6Q1/6pk/8 w - - 0 1", "solution": "1. Qf3 Ka4 2. Qb3+ Ka5 3. Qb5#"},
                {"fen": "8/8/8/8/5Q2/6p1/6pk/6K1 w - - 0 1", "solution": "1. Qf5 g2 2. Qe4 g1=Q 3. Qb7#"},
            ],
            "Мат в 4 хода": [
                {"fen": "8/8/8/8/8/5Q2/6pk/5K2 w - - 0 1", "solution": "1. Qf5 g5 2. Qe4 g4 3. Qd3 g3 4. Qb5#"},
                {"fen": "8/8/8/8/5K2/6Q1/6p1/6k1 w - - 0 1", "solution": "1. Qf2 g5 2. Qe3 g4 3. Qd2 g3 4. Qf2#"},
            ]
        }

IMAGE_PATH = r'C:\Users\FuckFaceOfNorth\PycharmProjects\TANDD\images'

piece_images = {
    'p': 'black_pawn.png',
    'r': 'black_rook.png',
    'n': 'black_knight.png',
    'b': 'black_bishop.png',
    'q': 'black_queen.png',
    'k': 'black_king.png',
    'P': 'white_pawn.png',
    'R': 'white_rook.png',
    'N': 'white_knight.png',
    'B': 'white_bishop.png',
    'Q': 'white_queen.png',
    'K': 'white_king.png',
}

user_states = {}
stats = {"tasks_requested": 0}


def generate_chess_position(fen: str, output_path: str):
    board_image = Image.open(f"{IMAGE_PATH}/board.png")
    square_size = board_image.width // 8
    rows = fen.split(" ")[0].split("/")

    for row_idx, row in enumerate(rows):
        col_idx = 0
        for char in row:
            if char.isdigit():
                col_idx += int(char)
            else:
                piece_image = Image.open(f"{IMAGE_PATH}/{piece_images[char]}")
                x = col_idx * square_size
                y = row_idx * square_size
                board_image.paste(piece_image, (x, y), piece_image)
                col_idx += 1

    turn = fen.split(" ")[1]
    draw = ImageDraw.Draw(board_image)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    if turn == "w":
        draw.text((5, board_image.height - 20), "a", fill="black", font=font)
        draw.text((square_size // 2, board_image.height - 20), "1", fill="black", font=font)
        draw.text((board_image.width - square_size + 5, 5), "h", fill="black", font=font)
        draw.text((board_image.width - square_size // 2, 5), "8", fill="black", font=font)
    else:
        draw.text((5, board_image.height - 20), "h", fill="black", font=font)
        draw.text((square_size // 2, board_image.height - 20), "8", fill="black", font=font)
        draw.text((board_image.width - square_size + 5, 5), "a", fill="black", font=font)
        draw.text((board_image.width - square_size // 2, 5), "1", fill="black", font=font)

    board_image.save(output_path)


task_menu = ReplyKeyboardMarkup([
    ['Мат в 1 ход', 'Мат в 2 хода'],
    ['Мат в 3 хода', 'Мат в 4 хода'],
    ['Назад']
], resize_keyboard=True)

problem_menu = ReplyKeyboardMarkup([
    ['Следующая задача', 'Назад']
], resize_keyboard=True)

main_menu = ReplyKeyboardMarkup([
    ['Решить задачу'],
], resize_keyboard=True)


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Добро пожаловать в шахматного бота! Выберите действие:",
        reply_markup=main_menu
    )


async def stats_command(update: Update, context: CallbackContext) -> None:
    YOUR_ADMIN_ID = 123456789  # Замените на ваш Telegram ID
    if update.message.from_user.id == YOUR_ADMIN_ID:
        await update.message.reply_text(f"Задач запрошено: {stats['tasks_requested']}")
    else:
        await update.message.reply_text("Эта команда доступна только администратору.")


async def send_chess_problem(update: Update, context: CallbackContext, task: dict, task_type: str) -> None:
    output_path = f"output_chess_position_{update.message.from_user.id}.png"
    generate_chess_position(task["fen"], output_path)
    turn = task["fen"].split(" ")[1]
    turn_text = "Ход белых" if turn == "w" else "Ход чёрных"
    description = f"{turn_text}, {task_type.lower()}."
    with open(output_path, 'rb') as img:
        await update.message.reply_photo(img, caption=description)
    os.remove(output_path)


async def handle_buttons(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    user_id = update.message.from_user.id

    if text == 'Решить задачу':
        await update.message.reply_text("Выберите тип задачи:", reply_markup=task_menu)
    elif text in ['Мат в 1 ход', 'Мат в 2 хода', 'Мат в 3 хода', 'Мат в 4 хода']:
        task_type = text
        if user_id not in user_states:
            user_states[user_id] = {"task_type": task_type, "used_fens": []}
        available_tasks = [t for t in tasks[task_type] if t["fen"] not in user_states[user_id]["used_fens"]]
        if not available_tasks:
            user_states[user_id]["used_fens"] = []
            available_tasks = tasks[task_type]
        task = random.choice(available_tasks)
        user_states[user_id]["task_type"] = task_type
        user_states[user_id]["used_fens"].append(task["fen"])
        stats["tasks_requested"] += 1
        await send_chess_problem(update, context, task, task_type)
        await update.message.reply_text("Что дальше?", reply_markup=problem_menu)
    elif text == 'Назад':
        if user_id in user_states:
            del user_states[user_id]
            await update.message.reply_text("Выберите тип задачи:", reply_markup=task_menu)
        else:
            await update.message.reply_text("Возвращаюсь в главное меню", reply_markup=main_menu)
    elif text == 'Следующая задача' and user_id in user_states:
        task_type = user_states[user_id]["task_type"]
        available_tasks = [t for t in tasks[task_type] if t["fen"] not in user_states[user_id]["used_fens"]]
        if not available_tasks:
            user_states[user_id]["used_fens"] = []
            available_tasks = tasks[task_type]
        task = random.choice(available_tasks)
        user_states[user_id]["used_fens"].append(task["fen"])
        stats["tasks_requested"] += 1
        await send_chess_problem(update, context, task, task_type)
        await update.message.reply_text("Что дальше?", reply_markup=problem_menu)


async def error_handler(update: Update, context: CallbackContext) -> None:
    if isinstance(context.error, NetworkError):
        print(f"Сетевая ошибка: {context.error}. Повторяем попытку через 5 секунд...")
        await asyncio.sleep(5)


if __name__ == '__main__':
    TOKEN = '6660059811:AAFztgI9SBUogHKMeiNEk_NgL1CXbaB5vSo'
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stats', stats_command))
    button_filter = filters.TEXT & ~filters.COMMAND & filters.Regex(
        r'^(Решить задачу|Мат в 1 ход|Мат в 2 хода|Мат в 3 хода|Мат в 4 хода|Назад|Следующая задача)$'
    )
    app.add_handler(MessageHandler(button_filter, handle_buttons))
    app.add_error_handler(error_handler)

    app.run_polling()