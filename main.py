import pandas as pd
import sqlite3
#import requests
from requests import *

con = sqlite3.connect("store.sqlite")
f_damp = open('store.db', 'r', encoding = 'utf-8-sig')
damp = f_damp.read()
f_damp.close()
con.executescript(damp)
con.commit()
cursor = con.cursor()

cursor.execute('''
SELECT buy.buy_id as Заказ, city.name_city as Город, book.title as Книга, buy_book.amount as Количество
FROM buy, client, book, buy_book, buy_step, city
WHERE 
buy.buy_id = buy_step.buy_id AND
buy_step.step_id = 4 AND
buy_step.date_step_end <= DATE('now') AND
client.client_id = buy.client_id AND
client.city_id = city.city_id AND
buy.buy_id = buy_book.buy_id AND
buy_book.book_id = book.book_id
ORDER BY
buy.buy_id, book.title ASC
             '''
)

print(cursor.fetchall())

cursor.execute('''
SELECT buy.buy_id as Заказ, SUBSTR(client.name_client, 1, INSTR(client.name_client, ' ')) as Клиент, SUM(book.price * buy_book.amount) as Стоимость
FROM client, buy, buy_book, book
WHERE client.client_id = buy.client_id AND
buy.buy_id = buy_book.buy_id AND
buy_book.book_id = book.book_id
GROUP BY 
client.name_client
HAVING
SUM(book.price * buy_book.amount) >= 2000 OR
SUM(book.price * buy_book.amount) <= 500
ORDER BY 
SUM(book.price * buy_book.amount) DESC, client.name_client ASC
''')

print(cursor.fetchall())

cursor.execute('''
with genre_amount as(
select
genre.genre_id as g,
SUM(buy_book.amount) as a

from buy_book, book, genre
WHERE
genre.genre_id = book.genre_id AND
buy_book.book_id = book.book_id
GROUP BY
g
)
select book.title as название from genre_amount, book
WHERE book.genre_id = g AND
a=(select MAX(a) from genre_amount)
''')

print(cursor.fetchall())

avg_sold_query = '''
WITH AvgSold AS (
    SELECT 
        bb.book_id,
        COUNT(bb.buy_book_id) AS total_sold,
        AVG(COUNT(bb.buy_book_id)) OVER () AS avg_sold
    FROM 
        buy_book bb
    GROUP BY 
        bb.book_id
)

UPDATE book
SET price = 
    CASE 
        WHEN b.total_sold > a.avg_sold THEN
            ROUND(price * 1.1, 2)
        ELSE
            ROUND(price * 0.95, 2)
    END
FROM (
    SELECT bb.book_id, COUNT(bb.buy_book_id) AS total_sold
    FROM buy_book bb
    GROUP BY bb.book_id
) b
JOIN AvgSold a ON b.book_id = a.book_id;
'''

# Выполняем обновление цен
cursor.execute(avg_sold_query)

# Выводим обновленные цены
select_query = '''
SELECT * FROM book;
'''
cursor.execute(select_query)
print(cursor.fetchall())

report = '''
WITH RankedBooks AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY amount DESC) AS "Nпп",
        SUBSTR(title, 1, 12) || '...' AS "Книга",
        name_author AS "Автор",
        amount AS "Кол-во",
        RANK() OVER (ORDER BY amount DESC) AS "Ранг",
        PERCENT_RANK() OVER (ORDER BY amount DESC) AS "Ранг,%",
        SUM(amount) OVER (ORDER BY amount DESC) AS "Распределение"
    FROM book
    JOIN author ON book.author_id = author.author_id
)
SELECT
    "Nпп",
    "Автор",
    "Книга",
    "Кол-во",
    "Ранг",
    "Распределение",
    ROUND("Ранг,%", 2) AS "Ранг,%"
FROM RankedBooks
ORDER BY "Кол-во" DESC;
'''

cursor.execute(report)

print(cursor.fetchall())

con.close()
