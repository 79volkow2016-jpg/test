import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Базовая настройка логирования, чтобы ошибки писались в консоль
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Защита от запуска без токена
if not TOKEN:
    raise ValueError("Ошибка: Токен бота не найден. Проверьте файл .env!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")

# Фото, которое получают при любом неверном (и частично верном) ответе.
WRONG_PHOTO = "wrong.jpg"

QUESTIONS = [
    {
        "text": "Какой у него любимый трек, если музыкальный вкус вообще пережил встречу с плейлистом, блядь?",
        "options": [
            "Пицца — круглый хит для желудка",
            "«Чё нахуй» — вот это уже музыкальная душа",
            "Джамшут: саундтрек к переезду дивана",
            "«Такси два» — ремикс «куда едем, блядь?»",
        ],
        "replies": [
            "это не трек, блядь, а круглая жратва. Хотя на сломанном проигрывателе и не такое говно крутят. ",
            "Охуеть, угадал! Палец впервые за день ткнул не в какую-то херню. ",
            " мимо, нахуй. Звучит так, будто сейчас диван вынесет, а ты ему даже спасибо не скажешь. ",
            "Такси два — мимо. Вызвал ответ, а приехала херня без сдачи. ",
        ],
        "correct": [1],
        "photo": "q1.jpg",
    },
    {
        "text": "Чем он занимается по выходным? (можно несколько: диван уже подал заявление на совместное проживание, пиздец)",
        "options": [
            "Жрёт БК, будто там выдают паспорт",
            "Ввязался в сомнительную движуху и зовёт это отдыхом",
            "Бегает — если холодильник сам покатился",
            "Носится куда-то, а зачем — хрен его знает",
        ],
        "replies": [
            "Бургер Кинг — его вторая родина, блядь. Паспорт уже жирный, а корона из картошки фри. ",
            "За такой вариант даже викторина охуела и просит не втягивать её в эту херню. ",
            "Бегает? Ага, нахуй. Только если холодильник сам покатился к соседям. ",
            "«Спид» — мимо, блядь. Куда гнал, если всё равно ответ хреновый? ",
        ],
        "correct": [0, 1],
        "photo": "q2.jpg",
    },
    {
        "text": "Какое у него главное хобби, кроме уверенно раздавать советы, которых никто не просил, нахуй?",
        "options": [
            "Футбол: орёт на телик, будто тот ему должен",
            "«gbdj» — пароль от холодильника, набранный лбом",
            "Пиво — хобби, собеседник и, кажется, лучший друг",
        ],
        "replies": [
            "Футбол — его хобби, если орать на телик и жрать чипсы — олимпийский вид спорта, блядь. ",
            "«gbdj» — это пароль от холодильника или ты тест мордой об клавиатуру прошёл? ",
            "Пиво — его хобби. Кружка уже заебалась слушать его пьяный стендап. ",
        ],
        "correct": [2],
        "photo": "q3.jpg",
    },
    {
        "text": "Что его бесит? (можно несколько: кроме этого вопроса и людей с хорошей памятью, блядь)",
        "options": [
            "Рэп — рифмы мешают ему нести свою хуйню",
            "«Такси два» — когда даже маршрут бесит",
            "Пиво — единственный, кто его пока не раздражает",
            "Ранний подъём — личное объявление войны будильнику",
        ],
        "replies": [
            "Рэп его бесит, блядь. Видимо, рифмы напоминают, что он сам связать два слова не может. ",
            "Такси два — мимо, нахуй. Заказал ответ, приехала какая-то ебанина без навигатора. ",
            "Пиво его не бесит — они с кружкой давно всё обсудили и послали тебя к чёрту. ",
            "Ранний подъём — враг. Будильник орёт, он лежит и шлёт весь мир нахуй. ",
        ],
        "correct": [0, 3],
        "photo": "q4.jpg",
    },
]
QUESTIONS.extend([
    {
        "text": "Тима на паре, препод спрашивает тему, которую он не учил. Какой академический пиздец он устроит?",
        "options": [
            "Несёт уверенную хуйню с лицом профессора",
            "Включает режим «я мебель, не спрашивайте»",
            "Уходит в туалет переждать этот учебный пиздец",
            "Честно говорит «не готов» — чудо, блядь, века",
        ],
        "replies": [
            "Уверенность решает 90% его экзаменов, красавчик ",
            "Мимо, он не призрак, его всегда видно и слышно ",
            "Сорок минут? Он вернётся к звонку, мудила ",
            "Честно?! Ты вообще Тиму знаешь, долбоёб? ",
        ],
        "correct": [0],
        "photo": "q5.jpg",
    },
    {
        "text": "Тима стал президентом — держитесь, страна. Что попадёт в первый указ? (можно несколько)",
        "options": [
            "Бесплатный БК — бюджет страны плачет, Тима счастлив",
            "Запретить ранний подъём под страхом будильника",
            "Поджукник — гос. язык, переводчик не предусмотрен",
            "Закрыть все универы, чтоб не палили его прогулы",
        ],
        "replies": [
            "БК бесплатно — народ в слезах, Тима красавчик ",
            "Ранний подъём под запретом, это святое ",
            "Поджукник главным словом страны, и чтоб все учили ",
            "Универы закрыть? Он сам там учится, дебил ",
        ],
        "correct": [0, 1, 2],
        "photo": "q6.jpg",
    },
    {
        "text": "Что такое «поджукник» — термин из науки или очередная хуйня, понятная только вам двоим?",
        "options": [
            "Профессия, которой нет, как и его плана на завтра",
            "Научный термин, который учёные уже просят забыть",
            "Слово, придуманное вами вдвоём — и хрен объяснишь людям",
            "Блюдо из БК, которое даже кассир боится пробивать",
        ],
        "replies": [
            "Профессии нет, а такие мудаки есть ",
            "В универе такое не проходят, и слава богу ",
            "Да. Остальным объяснять бесполезно, они не вывезут ",
            "Из БК только вонючая хуйня, ты чего ",
        ],
        "correct": [2],
        "photo": "q7.jpg",
    },
    {
        "text": "Какие фразы Тима повторяет ежедневно, будто за каждое «чё нахуй» ему платят? (можно несколько)",
        "options": [
            "«Ну так-то» — разгон перед очередной хуйнёй",
            "«Чё нахуй» — официальный гимн растерянности",
            "«Поджукник» — слово, после которого всем нужен переводчик",
            "«Я не виноват» — алиби, заготовленное заранее",
        ],
        "replies": [
            "«Ну так-то» — слово-паразит, которое у него точно есть ",
            "«Чё нахуй» — гимн его жизни, ты слышал это сто раз ",
            "Поджукник — наше всё, тут без вопросов ",
            "«Я не виноват» — его визитная карточка, даже не краснеет ",
        ],
        "correct": [1, 2, 3],
        "photo": "q8.jpg",
    },
    {
        "text": "Что Тима скажет, если разбудить его в семь утра — кроме всего матного говна, что цензура не пропустит?",
        "options": [
            "«Доброе утро» — и все понимают, что это не Тима",
            "«Ты чё, ахуел?» — прогноз погоды на ближайшие пять минут",
            "Молча испепелит взглядом, потом всё равно пошлёт нахуй",
            "Не проснётся, хоть оркестр под ухом ебашь",
        ],
        "replies": [
            "«Доброе утро»?! Этого человека ты видишь в первый раз ",
            "Классика. Сначала мат, потом уже глаза открываются ",
            "Взгляд убийственный, но мат всё равно будет первым ",
            "Не проснётся — а нахуя тогда будить, дебил ",
        ],
        "correct": [1],
        "photo": "q9.jpg",
    },
    {
        "text": "Самара, три ночи, Тима на улице. Какой движ он мутит, пока нормальные люди спят? (можно несколько, нахуй)",
        "options": [
            "Ищет, где ещё кормят и не задают лишних вопросов",
            "Звонит тебе, чтобы сообщить важное «да так, ничё»",
            "Втюхивает прохожему теорию поджукника — держись, прохожий",
            "Лежит на лавке и правит Самарой в одиночку",
        ],
        "replies": [
            "Что-нибудь открытое он найдёт, нюх как у крысы ",
            "Звонит просто так, чтобы сказать хуйню и сбросить ",
            "Прохожий уже ничего не понял, а Тима доволен ",
            "Король города на лавке — всё как обычно, ничего нового ",
        ],
        "correct": [0, 1, 2],
        "photo": "q10.jpg",
    },
    {
        "text": "Кто вытащит Тиму из очередной жопы, куда он влез с видом «я всё контролирую»?",
        "options": [
            "Мясник — придёт с лицом «кто тут опять накосячил?»",
            "Природа — молча посмотрит, и всем станет неловко",
            "Прокачка — составит гениальный план и забудет его",
            "Быков — наорёт так, что проблема сама свалит",
        ],
        "replies": [
            "Мясник придёт и решит вопрос лицом, без лишних слов ",
            "Природа выйдет, молча посмотрит на всех, и все всё поймут ",
            "Прокачка прокачает план до максимума и забудет прийти ",
            "Быков придёт, наорёт на всех и всё порешает ",
        ],
        "correct": [3],
        "photo": "q11.jpg",
    },
    {
        "text": "Что Тима делает, когда ему скучно и мозг опять ушёл покурить? (можно несколько)",
        "options": [
            "Идёт жрать — мозг молчит, желудок командует",
            "Пишет «го гулять» и исчезает, как должник",
            "Смотрит рилсы до рассвета, а потом винит понедельник",
            "Читает умные книжки — вот это уже фантастика",
        ],
        "replies": [
            "Жрать — универсальный ответ на любую проблему ",
            "Всех поднял, а сам лёг обратно. Классика мудака ",
            "Рассвет он встречает с телефоном в руке, пиздец ",
            "Умные книжки?? Ты ахуел или шутишь, нахуй? ",
        ],
        "correct": [0, 1, 2],
        "photo": "q12.jpg",
    },
    {
        "text": "Что на языке Тимы означает «щас буду» — кроме «не ставь воду, я ещё лежу, блядь»?",
        "options": [
            "Минут через десять — по его часам, не по земным",
            "Через час — если звёзды и доставка сойдутся",
            "Он ещё в кровати, блядь, и даже не ищет носки",
            "Не придёт, но будет писать «уже выхожу»",
        ],
        "replies": [
            "Десять минут?! Ты оптимист, мудак ",
            "Час — это если ему сильно повезёт",
            "Ещё и одеялом накрылся. В точку ",
            "Похоже, но сначала он всё-таки дойдёт до порога ",
        ],
        "correct": [2],
        "photo": "q13.jpg",
    },
    {
        "text": "Что выдаёт Тима, когда его поймали за руку, а план «я ни при чём» уже трещит? (можно несколько)",
        "options": [
            "«Это не я» — сказал человек с уликой в руке",
            "«Ну а чё» — защита уровня «мамой клянусь»",
            "«Это Мясник» — универсальный перевод стрелок",
            "«Поджукник виноват» — суд закрыл дело от смеха",
        ],
        "replies": [
            "«Это не я» — и сам себе не верит ",
            "«Ну а че» — универсальный ответ на всё на свете ",
            "Свалить на Мясника — это святое, пацаны поймут ",
            "Поджукник виноват — ну это уже совсем пиздец ",
        ],
        "correct": [1, 2],
        "photo": "q14.jpg",
    },
    {
        "text": "Тиме дали миллион и сутки. Как быстро деньги превратятся в легенду о том, что их, нахуй, вообще когда-то видели?",
        "options": [
            "Купит БК целиком — и будет просить сдачу с кассы",
            "Раздаст пацанам, займёт обратно и снова уйдёт в минус",
            "Накупит всем кликух — будто старых проблем мало",
            "Спрячет деньги так надёжно, что сам их проебёт",
        ],
        "replies": [
            "Целиком не купит, у него на это пороху не хватит ",
            "Раздаст, займёт обратно, а к вечеру опять в минусе. В точку ",
            "Кликухи он и так раздаёт бесплатно, нахуя покупать ",
            "Спрячет и забудет — финал в его стиле, но не сегодня ",
        ],
        "correct": [1],
        "photo": "q15.jpg",
    },
])


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Пройти тест", callback_data="quiz")],
    ])


def score_question(q, selected):
    correct = set(q["correct"])
    right = len(selected & correct)
    wrong = len(selected - correct)
    return max(0, (right - wrong) / len(correct))


def verdict(score):
    if score == 1:
        return "Правильно!"
    if score == 0:
        return "Неправильно."
    return "Частично верно."


def mark(score):
    if score == 1:
        return "+"
    if score == 0:
        return "-"
    return "~"


def result_comment(percent):
    if percent >= 90:
        return "Ого, да ты эксперт по Тимологии! Знаешь его лучше, чем он сам."
    if percent >= 60:
        return "Неплохо, ты определенно в теме. Почти доверенное лицо."
    if percent >= 30:
        return "Есть над чем поработать. Видимо, ты видел его только издалека."
    return "Полный провал. Ты точно знаком с Тимой?"


async def send_screen(query, context, text, markup, photo_name=None):
    """Убирает старое сообщение и присылает новое: с фото или текстом."""
    chat_id = query.message.chat_id
    try:
        await query.message.delete()
    except Exception:
        pass

    path = os.path.join(PHOTOS_DIR, photo_name) if photo_name else None

    # ИСПРАВЛЕНИЕ: Telegram API умеет сам принимать путь к файлу.
    # Больше нет блокирующего with open(path, "rb")!
    if path and os.path.isfile(path):
        await context.bot.send_photo(chat_id=chat_id, photo=path, caption=text, reply_markup=markup)
    else:
        if photo_name:
            logger.warning(f"Photo not found: {path}")
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Добро пожаловать в викторину о Тиме. Давай проверим, насколько хорошо ты ориентируешься в его странностях:",
        reply_markup=main_menu(),
    )


async def show_question(query, context):
    ud = context.user_data
    q = QUESTIONS[ud["q"]]
    multi = len(q["correct"]) > 1
    rows = []
    for i, option in enumerate(q["options"]):
        if multi:
            marker = "[x] " if i in ud["selected"] else "[ ] "
            label = marker + option
        else:
            label = option
        rows.append([InlineKeyboardButton(label, callback_data=f"opt:{i}")])
    if multi:
        rows.append([InlineKeyboardButton("Готово", callback_data="done")])
    text = f"Вопрос {ud['q'] + 1} из {len(QUESTIONS)}\n\n{q['text']}"
    await send_screen(query, context, text, InlineKeyboardMarkup(rows))


async def show_feedback(query, context, q, score):
    ud = context.user_data
    text = verdict(score) + "\n\n"

    replies = q.get("replies", [])
    lines = []
    for i in sorted(ud["selected"]):
        if i < len(replies):
            lines.append(f"• {replies[i].strip()}")
    if lines:
        text += "\n".join(lines) + "\n\n"

    explain = q.get("explain", "")
    if explain:
        text += explain

    photo = q.get("photo") if score == 1 else WRONG_PHOTO

    is_last = ud["q"] == len(QUESTIONS) - 1
    button_text = "показать на сколько мы кенты" if is_last else "летс гоу"
    buttons = [InlineKeyboardButton(button_text, callback_data="next")]
    if score < 1:
        buttons.append(InlineKeyboardButton("Попробовать ещё раз", callback_data="retry"))
    markup = InlineKeyboardMarkup([buttons])
    await send_screen(query, context, text.strip(), markup, photo_name=photo)


async def show_result(query, context):
    history = context.user_data["history"]
    if not history:
        percent = 0
    else:
        percent = round(sum(h["score"] for h in history) / len(history) * 100)
    attempts_by_question = {i: [] for i in range(len(QUESTIONS))}
    for attempt in history:
        attempts_by_question[attempt["q"]].append(attempt["score"])

    lines = [f"Твой результат: {percent}%", "", result_comment(percent), "", "Разбор:"]
    for n, q in enumerate(QUESTIONS, 1):
        answers = ", ".join(q["options"][i] for i in q["correct"])
        attempts = attempts_by_question[n - 1]
        if attempts:
            comments = []
            for attempt_number, score in enumerate(attempts):
                if score == 1:
                    comment = "безупречно"
                elif score == 0 and attempt_number > 0:
                    comment = "нужно больше стараться"
                elif score == 0:
                    comment = "мимо"
                else:
                    comment = "почти попал"
                comments.append(f"{mark(score)} {comment}")
            attempt_text = " → ".join(comments)
        else:
            attempt_text = "не отвечал"
        lines.append(f"{n}. {q['text']}\n   Попытки: {attempt_text}\n   Верный ответ: {answers}")

    context.user_data.clear()

    # Объединяем строки.
    # В Telegram лимит 4096 символов. Если вопросов будет больше 20,
    # придется разбивать на 2 сообщения, но для 15 вопросов должно хватить.
    final_text = "\n".join(lines)
    await send_screen(query, context, final_text, main_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    ud = context.user_data

    if data == "quiz":
        ud.clear()
        ud["q"] = 0
        ud["selected"] = set()
        ud["history"] = []
        ud["answered"] = False
        await show_question(query, context)
        return

    if data.startswith("opt:") or data in {"done", "next", "retry"}:
        if "q" not in ud:
            await send_screen(query, context, "Начни заново:", main_menu())
            return

        if data == "retry":
            if not ud["answered"]:
                return
            ud["answered"] = False
            ud["selected"] = set()
            await show_question(query, context)
            return

        if data == "next":
            if not ud["answered"]:
                return
            ud["answered"] = False
            ud["q"] += 1
            ud["selected"] = set()
            if ud["q"] < len(QUESTIONS):
                await show_question(query, context)
            else:
                await show_result(query, context)
            return

        if ud["answered"]:
            return  # ответ уже принят, ждём перехода или повтора

        q = QUESTIONS[ud["q"]]
        multi = len(q["correct"]) > 1
        if data.startswith("opt:"):
            i = int(data.split(":")[1])
            if multi:
                ud["selected"] ^= {i}
                await show_question(query, context)
                return
            ud["selected"] = {i}
        elif multi and not ud["selected"]:
            return  # нажали «Готово», ничего не выбрав

        score = score_question(q, ud["selected"])
        ud["history"].append({"q": ud["q"], "score": score})
        ud["answered"] = True
        await show_feedback(query, context, q, score)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()


if __name__ == "__main__":
    main()