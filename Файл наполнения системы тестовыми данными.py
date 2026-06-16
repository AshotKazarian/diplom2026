import os
import random

import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thesis_system.settings")
django.setup()

from django.contrib.auth.models import Group

from accounts.models import Professor, QuotaChangeRequest, Student, User
from applications.models import ThesisApplication
from references.models import (Degree, Department, Faculty, Position, Profile,
                               Rank)
from technologies.models import Technology, TechnologyCategory

# ========== 1. НАСТРОЙКИ ==========

STUDENTS_PER_GROUP = 20
GROUPS_PER_FACULTY = 3

# Кафедры, профили и технологии
TEST_DEPARTMENTS = [
    {
        "name": "Инфокогнитивные технологии",
        "faculty_name": "Информационных технологий",
        "profile_name": "Информационные технологии управления бизнесом",
        "education_code": "09.03.03",
        "education_specialty": "Прикладная информатика",
        "technologies": [
            "FastAPI",
            "React",
            "PostgreSQL",
            "Docker",
            "Pandas",
            "Scikit-learn",
        ],
        "tech_category": "Веб-фреймворки и анализ данных",
    },
    {
        "name": "Прикладная информатика",
        "faculty_name": "Информационных технологий",
        "profile_name": "Прикладная информатика",
        "education_code": "09.03.03",
        "education_specialty": "Прикладная информатика",
        "technologies": ["Spring Boot", "Java", "Hibernate", "MySQL", "Maven", "Git"],
        "tech_category": "Корпоративная разработка",
    },
    {
        "name": "Информационная безопасность",
        "faculty_name": "Информационных технологий",
        "profile_name": "Информационная безопасность",
        "education_code": "10.03.01",
        "education_specialty": "Информационная безопасность",
        "technologies": [
            "Wireshark",
            "Metasploit",
            "OpenSSL",
            "Nmap",
            "Bash",
            "Python",
        ],
        "tech_category": "Сетевые технологии и безопасность",
    },
]

# Данные для генерации
LAST_NAMES_MALE_PROF = [
    "Иванов",
    "Смирнов",
    "Кузнецов",
    "Попов",
    "Васильев",
    "Петров",
    "Соколов",
    "Михайлов",
    "Новиков",
    "Фёдоров",
    "Морозов",
    "Волков",
]
LAST_NAMES_FEMALE_PROF = [
    "Иванова",
    "Смирнова",
    "Кузнецова",
    "Попова",
    "Васильева",
    "Петрова",
    "Соколова",
    "Михайлова",
    "Новикова",
    "Фёдорова",
    "Морозова",
    "Волкова",
]

LAST_NAMES_MALE_STUD = [
    "Иванов",
    "Смирнов",
    "Кузнецов",
    "Попов",
    "Васильев",
    "Петров",
    "Соколов",
    "Михайлов",
    "Новиков",
    "Фёдоров",
]
LAST_NAMES_FEMALE_STUD = [
    "Иванова",
    "Смирнова",
    "Кузнецова",
    "Попова",
    "Васильева",
    "Петрова",
    "Соколова",
    "Михайлова",
    "Новикова",
    "Фёдорова",
]

FIRST_NAMES_MALE = [
    "Александр",
    "Дмитрий",
    "Максим",
    "Сергей",
    "Андрей",
    "Алексей",
    "Артём",
    "Илья",
    "Кирилл",
    "Никита",
]
FIRST_NAMES_FEMALE = [
    "Анна",
    "Елена",
    "Татьяна",
    "Ольга",
    "Мария",
    "Ирина",
    "Светлана",
    "Наталья",
    "Екатерина",
    "Юлия",
]
PATRONYMICS_MALE = [
    "Александрович",
    "Дмитриевич",
    "Сергеевич",
    "Андреевич",
    "Алексеевич",
    "Ильич",
    "Михайлович",
    "Владимирович",
]
PATRONYMICS_FEMALE = [
    "Александровна",
    "Дмитриевна",
    "Сергеевна",
    "Андреевна",
    "Алексеевна",
    "Ильинична",
    "Михайловна",
    "Владимировна",
]

# Должности с разными весами
POSITIONS_WITH_WEIGHTS = [
    ("Профессор", 1),
    ("Доцент", 3),
    ("Старший преподаватель", 4),
    ("Преподаватель", 2),
    ("Ассистент", 1),
]

DEGREE_NAMES = ["Доктор наук", "Кандидат наук", "Без степени"]
RANK_NAMES = ["Профессор", "Доцент", "Без звания"]

# Квота преподавателя
PROFESSOR_MAX_LOAD_MIN = 10
PROFESSOR_MAX_LOAD_MAX = 12

# Количество заявок на студента
APPLICATIONS_PER_STUDENT_MIN = 1
APPLICATIONS_PER_STUDENT_MAX = 2

# Вероятности статусов
STATUS_WEIGHTS = {
    "approved": 0.6,
    "sent": 0.2,
    "rejected": 0.1,
    "withdrawn": 0.1,
}

# Список возможных областей научных интересов
RESEARCH_INTERESTS = [
    "Искусственный интеллект, машинное обучение, анализ данных",
    "Разработка веб-приложений, веб-фреймворки, микросервисы",
    "Информационная безопасность, криптография, защита данных",
    "Базы данных, SQL, NoSQL, оптимизация запросов",
    "Мобильная разработка, iOS, Android, Flutter",
    "Облачные технологии, DevOps, контейнеризация",
    "Компьютерное зрение, обработка изображений",
    "Естественно-языковая обработка текстов (NLP)",
    "Распределённые системы, высоконагруженные приложения",
    "Тестирование ПО, автоматизация тестирования",
    "Управление IT-проектами, Agile, Scrum",
    "Бизнес-аналитика, BI-системы, Data Science",
]

# ========== 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========


def transliterate(text):
    translit_dict = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ё": "E",
        "Ж": "Zh",
        "З": "Z",
        "И": "I",
        "Й": "Y",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "H",
        "Ц": "Ts",
        "Ч": "Ch",
        "Ш": "Sh",
        "Щ": "Sch",
        "Ъ": "",
        "Ы": "Y",
        "Ь": "",
        "Э": "E",
        "Ю": "Yu",
        "Я": "Ya",
    }
    result = []
    for char in text:
        result.append(translit_dict.get(char, char))
    return "".join(result)


def generate_username(last_name, first_name, patronymic, used_usernames):
    base = transliterate(last_name).lower()
    i = transliterate(first_name[0]).lower()
    o = transliterate(patronymic[0]).lower()
    username = f"{base}.{i}.{o}"

    counter = 1
    original_username = username
    while username in used_usernames:
        username = f"{original_username}{counter}"
        counter += 1

    used_usernames.add(username)
    return username


def generate_full_name(last_name, first_name, patronymic):
    return f"{last_name} {first_name} {patronymic}"


def generate_phone():
    return f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"


def get_random_position():
    positions = []
    weights = []
    for pos, weight in POSITIONS_WITH_WEIGHTS:
        positions.append(pos)
        weights.append(weight)
    return random.choices(positions, weights=weights)[0]


def get_unique_last_name_for_prof(gender, used_names):
    available_names = []
    if gender == "male":
        for name in LAST_NAMES_MALE_PROF:
            if name not in used_names:
                available_names.append(name)
    else:
        for name in LAST_NAMES_FEMALE_PROF:
            if name not in used_names:
                available_names.append(name)

    if available_names:
        chosen = random.choice(available_names)
        used_names.add(chosen)
        return chosen
    else:
        return random.choice(
            LAST_NAMES_MALE_PROF if gender == "male" else LAST_NAMES_FEMALE_PROF
        )


def add_history_entry(application, user, action, details=""):
    if not application.history:
        application.history = []

    entry = {
        "timestamp": timezone.localtime(timezone.now()).strftime("%d.%m.%Y %H:%M"),
        "user_name": user.get_full_name() or user.username,
        "user_role": "Студент" if user.role == "student" else "Преподаватель",
        "action": action,
        "details": details,
    }
    application.history.append(entry)
    application.save(update_fields=["history"])


# ========== 3. ОСНОВНАЯ ФУНКЦИЯ ==========


def generate_test_data():
    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ ДЛЯ СИСТЕМЫ ВКР")
    print("=" * 70 + "\n")

    # Создаём группу для заведующих кафедры
    group, created = Group.objects.get_or_create(name="Заведующий кафедры")
    if created:
        print("✓ Создана группа 'Заведующий кафедры'")

    # Создаём факультеты
    faculties = {}
    for dept_info in TEST_DEPARTMENTS:
        faculty_name = dept_info["faculty_name"]
        if faculty_name not in faculties:
            faculty, _ = Faculty.objects.get_or_create(name=faculty_name)
            faculties[faculty_name] = faculty
            print(f"✓ Факультет: {faculty_name}")

    # Создаём кафедры и профили
    departments = []
    for dept_info in TEST_DEPARTMENTS:
        faculty = faculties[dept_info["faculty_name"]]
        dept, _ = Department.objects.get_or_create(
            name=dept_info["name"], faculty=faculty
        )
        departments.append(dept)
        print(f"✓ Кафедра: {dept.name} ({faculty.name})")

        Profile.objects.get_or_create(
            name=dept_info["profile_name"],
            department=dept,
            defaults={
                "education_code": dept_info["education_code"],
                "education_specialty": dept_info["education_specialty"],
            },
        )

    # Создаём справочники
    for pos, _ in POSITIONS_WITH_WEIGHTS:
        Position.objects.get_or_create(name=pos)
    for deg in DEGREE_NAMES:
        Degree.objects.get_or_create(name=deg)
    for r in RANK_NAMES:
        Rank.objects.get_or_create(name=r)

    degree_objects = {deg.name: deg for deg in Degree.objects.all()}
    rank_objects = {rank.name: rank for rank in Rank.objects.all()}

    # Создаём технологии
    tech_categories = {}
    for dept_info in TEST_DEPARTMENTS:
        cat_name = dept_info["tech_category"]
        if cat_name not in tech_categories:
            tech_categories[cat_name] = []
        tech_categories[cat_name].extend(dept_info["technologies"])

    for cat_name, tech_list in tech_categories.items():
        cat, _ = TechnologyCategory.objects.get_or_create(name=cat_name)
        for tech in tech_list:
            Technology.objects.get_or_create(name=tech, category=cat)
        print(f"✓ Созданы технологии: {cat_name} — {', '.join(tech_list)}")

    used_usernames = set()
    used_prof_last_names_local = set()

    # Создаём преподавателей (по 8 на кафедру) с уникальными фамилиями
    professors = []
    for dept in departments:
        for i in range(8):
            gender = "male" if i % 2 == 0 else "female"
            if gender == "male":
                last = get_unique_last_name_for_prof("male", used_prof_last_names_local)
                first = random.choice(FIRST_NAMES_MALE)
                patronymic = random.choice(PATRONYMICS_MALE)
            else:
                last = get_unique_last_name_for_prof(
                    "female", used_prof_last_names_local
                )
                first = random.choice(FIRST_NAMES_FEMALE)
                patronymic = random.choice(PATRONYMICS_FEMALE)

            full_name = generate_full_name(last, first, patronymic)
            username = generate_username(last, first, patronymic, used_usernames)

            user = User.objects.create_user(
                username=username, password="test123", role="professor"
            )
            user.password_display = "test123"
            user.save()

            max_load = random.randint(PROFESSOR_MAX_LOAD_MIN, PROFESSOR_MAX_LOAD_MAX)

            # Выбираем случайную область научных интересов
            research_interests = random.choice(RESEARCH_INTERESTS)

            professor = Professor.objects.create(
                user=user,
                full_name=full_name,
                faculty=dept.faculty,
                department=dept,
                position=Position.objects.get(name=get_random_position()),
                degree=degree_objects[random.choice(DEGREE_NAMES)],
                rank=rank_objects[random.choice(RANK_NAMES)],
                max_load=max_load,
                current_load=0,
                email=f"{username}@mospolytech.ru",
                phone=generate_phone(),
                research_interests=research_interests,
            )
            professors.append(professor)
            print(f"✓ Преподаватель: {full_name} ({dept.name})")

    # Создаём учебные группы
    groups_list = []
    group_counter = 101
    for dept in departments:
        for _ in range(GROUPS_PER_FACULTY):
            group_name = f"221-{group_counter}"
            group_counter += 1
            groups_list.append((group_name, dept))

    # Создаём студентов
    students = []
    for group_name, dept in groups_list:
        for _ in range(STUDENTS_PER_GROUP):
            gender = random.choice(["male", "female"])
            if gender == "male":
                last = random.choice(LAST_NAMES_MALE_STUD)
                first = random.choice(FIRST_NAMES_MALE)
                patronymic = random.choice(PATRONYMICS_MALE)
            else:
                last = random.choice(LAST_NAMES_FEMALE_STUD)
                first = random.choice(FIRST_NAMES_FEMALE)
                patronymic = random.choice(PATRONYMICS_FEMALE)

            full_name = generate_full_name(last, first, patronymic)
            username = generate_username(last, first, patronymic, used_usernames)

            user = User.objects.create_user(
                username=username, password="test123", role="student"
            )
            user.password_display = "test123"
            user.save()

            profile = Profile.objects.filter(department=dept).first()

            student = Student.objects.create(
                user=user,
                full_name=full_name,
                group=group_name,
                faculty=dept.faculty,
                department=dept,
                profile=profile,
                email=f"{username}@student.mospolytech.ru",
                phone=generate_phone(),
            )
            students.append(student)
        print(f"✓ Группа {group_name} ({dept.name}) — {STUDENTS_PER_GROUP} студентов")

    # Создаём заявки
    applications = []
    topics = [
        "Разработка веб-приложения на Django",
        "Анализ и оптимизация бизнес-процессов",
        "Исследование методов машинного обучения",
        "Автоматизация документооборота",
        "Разработка мобильного приложения",
        "Анализ данных и визуализация",
        "Проектирование информационной системы",
        "Цифровая трансформация предприятия",
    ]

    # Для каждого студента создаём 1 заявку
    for student in students:
        dept_professors = [p for p in professors if p.department == student.department]

        if not dept_professors:
            continue

        professor = random.choice(dept_professors)

        status = random.choices(
            list(STATUS_WEIGHTS.keys()), weights=list(STATUS_WEIGHTS.values())
        )[0]

        if status == "approved":
            if professor.current_load < professor.max_load:
                professor.current_load += 1
                professor.save()
            else:
                status = "sent"

        app = ThesisApplication.objects.create(
            student=student,
            professor=professor,
            topic=random.choice(topics),
            description="Актуальность темы обусловлена необходимостью автоматизации процессов.",
            status=status,
            created_at=timezone.now(),
        )

        add_history_entry(
            app, student.user, "Заявка подана студентом", f"Тема: {app.topic}"
        )

        if status == "approved":
            add_history_entry(
                app, professor.user, "Заявка одобрена преподавателем", "Заявка одобрена"
            )
        elif status == "rejected":
            add_history_entry(
                app,
                professor.user,
                "Заявка отклонена преподавателем",
                "Заявка отклонена",
            )
        elif status == "withdrawn":
            app.withdrawn_by = "professor"
            app.save(update_fields=["withdrawn_by"])
            add_history_entry(
                app,
                professor.user,
                "Заявка отозвана преподавателем",
                "Отозвана преподавателем",
            )

        applications.append(app)

    print(f"\n✓ Создано заявок: {len(applications)}")

    # Создаём запросы на изменение квоты (по 1 на кафедру)
    for dept in departments:
        dept_professors = [p for p in professors if p.department == dept]
        if dept_professors:
            professor = random.choice(dept_professors)
            requested = professor.max_load + random.choice([1, 2])
            requested = min(requested, 32)

            if requested > professor.max_load:
                reason = random.choice(
                    [
                        "Увеличение учебной нагрузки",
                        "Дополнительные студенты на дипломное проектирование",
                    ]
                )

                QuotaChangeRequest.objects.create(
                    professor=professor,
                    requested_max_load=requested,
                    reason=reason,
                    status="pending",
                )

    # Назначаем заведующих кафедрой
    for dept in departments:
        dept_professors = [p for p in professors if p.department == dept]
        if dept_professors:
            head = dept_professors[0]
            if not head.user.groups.filter(name="Заведующий кафедры").exists():
                head.user.groups.add(group)
                head.user.is_staff = True
                head.user.save()
                print(f"✓ {head.full_name} назначен заведующим кафедры {dept.name}")

    print("\n" + "=" * 70)
    print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70)

    print("\nСтатистика по заявкам:")
    for status in ["approved", "sent", "rejected", "withdrawn"]:
        count = ThesisApplication.objects.filter(status=status).count()
        percent = count / len(applications) * 100 if applications else 0
        print(f"  {status}: {count} ({percent:.1f}%)")

    print("\nСтатистика по нагрузке преподавателей:")
    for prof in professors:
        print(f"  {prof.full_name}: {prof.current_load}/{prof.max_load} одобренных")


if __name__ == "__main__":
    generate_test_data()
