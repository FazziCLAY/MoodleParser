from pprint import pprint

from requests import session, get, Session
from bs4 import BeautifulSoup

import time
import json

import config


# OLD: https://stackoverflow.com/questions/11901846/beautifulsoup-a-dictionary-from-an-html-table
# NEW: https://gist.github.com/AO8/63b9a5acb9fb238cbed13a0269d14137
def bs4_table_to_dict(table):
    rows = table.findAll("tr")
    rows_to_ret = []
    for row in rows:
        csv_row = []
        for cell in row.findAll(["td", "th"]):
            csv_row.append(cell.get_text())

        rows_to_ret.append(csv_row)

    return rows_to_ret


def debug(msg):
    if (config.DEBUG == True or config.DEBUG == 1):
        print(f"[DEBUG] {msg}")


def get_auth_token(session: Session):
    url = config.EOS_AUTH_URL
    page_content = session.get(url,
                               headers={
                                   "User-Agent": config.USERAGENT
                               }).content
    soup = BeautifulSoup(page_content, "html.parser")
    token = soup.find("input", {"name": "logintoken"})["value"]
    return token


def auth_moodle(login, password, url_domain) -> Session():
    s = Session()
    token = get_auth_token(s)
    payload = {'anchor': '', 'logintoken': token, 'username': login, 'password': password, 'rememberusername': 1}
    r_2 = s.post(url=url_domain + "/login/index.php", data=payload)
    for i in r_2.text.splitlines():
        if "<title>" in i:
            debug(f"<title> debug: {i[15:-8:]}")
            break
    counter = 0
    for i in r_2.text.splitlines():
        if "loginerrors" in i or (0 < counter <= 3):
            counter += 1
            debug(i)
    return s


def get_user_id(session):
    # Получение user_id из
    # <a href="#" data-route="view-settings" data-route-param="34327" aria-label="Настройки" role="button">
    #                                 <i class="icon fa fa-cog fa-fw " aria-hidden="true"></i>
    #                             </a>
    initial = session.get("https://eos2.vstu.ru/my/")
    soup = BeautifulSoup(initial.content, "html.parser")
    user_id = soup.find("a", {"href": "#", "data-route": "view-settings", "role": "button"})["data-route-param"]
    debug(f"user_id: {user_id}")


def get_active_courses_ids(session, user_id):
    _ = session.get(f"https://eos2.vstu.ru/user/profile.php?id={user_id}")
    soup = BeautifulSoup(_.content, "html.parser")
    one_of_course = soup.find("a",
                              {"href": f"https://eos2.vstu.ru/user/view.php?id=34327&course={config.ONE_OF_COURSE_ID}"})
    debug(f"first: {one_of_course}")
    debug(f"first.parent.parent: {one_of_course.parent.parent}")
    to_ret = []
    for x in one_of_course.parent.parent:
        course_id = x.next_element["href"].split("=")[2]
        to_ret.append(course_id)

    return to_ret


def sum_kr(list):
    ret = {
        "score": 0,
        "skip": 0
    }

    for e in list:
        try:
            ret["score"] += int(e["score"])
        except:
            pass

        try:
            ret["skipped"] += int(e["skipped"])
        except:
            pass


    return ret


stat = {}


def populate_stat(course_id, course_name, first, second):
    global stat
    c = str(course_id)
    totalCourse = sum_kr([first, second])
    stat["timestamp"] = time.time()
    stat["courses"][c] = {
        "name": course_name,
        "first": first,
        "second": second,
        "total": totalCourse
    }
    stat["total"] = sum_kr([stat["total"], totalCourse])  # append 'total'


def setup_stat():
    global stat
    stat = {
        "total": {
            "skipped": 0,
            "score": 0
        },
        "courses": {
            # "id_of_course": {
            #     "total": {
            #         "skip": 1,
            #         "score": 40
            #     },
            #     "first": {
            #         "skip": 1,
            #         "score": 40
            #     },
            #     "second": {
            #         "skip": 1,
            #         "score": 40
            #     }
            # }
        }
    }


def main():
    setup_stat()
    s = auth_moodle(config.EOS_AUTH_LOGIN, config.EOS_AUTH_PASSWORD, config.EOS_AUTH_URL)
    user_id = get_user_id(s)
    courses = get_active_courses_ids(s, user_id)

    for course_id in courses:
        course_url = f"https://eos2.vstu.ru/course/view.php?id={course_id}"
        debug(f"course_url: {course_url}")

        _ = s.get(course_url)
        soup = BeautifulSoup(_.content, "html.parser")

        name = soup.find("div", {"class": "page-header-headings"}).next_element.text
        print(f"== {name} ==")

        tableHtml = soup.find("table", {"class": "generaltable"})
        table = None
        if tableHtml is not None:
            table = bs4_table_to_dict(tableHtml)
            debug(table)
            firstKr = {
                "score": table[1][1].split(" ")[0],
                "skipped": table[2][1].split(" ")[0]
            }
            secondKr = {
                "score": table[1][2].split(" ")[0],
                "skipped": table[2][2].split(" ")[0]
            }

            populate_stat(course_id, name, firstKr, secondKr)
            print(f"Первая КР: {firstKr}")
            print(f"Вторая КР: {secondKr}")

    filename = "result.json"
    print(f"Write to file: {filename}")
    json.dump(stat, open(filename, 'w'), indent=2, sort_keys=True, ensure_ascii=False)


if __name__ == '__main__':
    main()
    debug("Finish.")
