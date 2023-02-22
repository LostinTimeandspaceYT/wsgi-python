import random


def generate_id_number():
    return random.randint(0, 65535)


def generate_id_string():
    id_string = ""
    i = 0
    while i < 10:
        id_string += str(random.randint(0, 9))
        if i == 2 or i == 5:
            id_string += "-"
        i += 1
    return id_string


add_company = ("INSERT INTO Company "
               "(Name, Address, Phone, State)"
               "VALUES (%s, %s, %s, %s)")

add_studio = ("INSERT INTO Studio "
              "(Name, Address, Phone, State)"
              "VALUES (%s, %s, %s, %s)")

add_movie = ("INSERT INTO movie "
             "(m_title, genre, minutes, release_date, budget)"
             "VALUES (%s, %s, %i, %s, %d)")

add_director = ("INSERT INTO Director "
                "(Name_Full, Address, State, PhoneNum, Email)"
                "VALUES (%s, %s, %s, %s, %s)")

add_writer = ("INSERT INTO Writer "
              "(Name_Full, Address, State, PhoneNum, Email)"
              "VALUES (%s, %s, %s, %s, %s)")

add_director_movie = ("INSERT INTO DirectorMovie "
                      "(Dir_id, m_id)"
                      "VALUES (%s, &i)")

add_writer_movie = ("INSERT INTO WriterMovie "
                    "(Wri_id, m_id)"
                    "VALUES (%s, %i)")

add_actor = ("INSERT INTO Actor "
             "(Actor_Name, Phone, Address, State)"
             "VALUES (%s, %s, %s, %s)")

add_actor_movie = ("INSERT INTO "
                   "(Movie_ID, Actor_ID, Actor_Role, Actor_Character)"
                   "VALUES (%i, %i, %s, %s, %s)")

add_theater = ("INSERT INTO Theater "
               "(name, address, city, state, zip, phone, website)"
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")

add_theater_movie = ("INSERT INTO TheaterMovie "
                     "(theater_id, m_id, ticket_sales, start_date, end_date)"
                     "VALUES (%s, %i, %d, %s, %s)")
