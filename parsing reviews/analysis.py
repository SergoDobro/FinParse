import json, numpy, re
import pandas as pd
from collections import Counter
import plotly.express as px
import matplotlib.pyplot as plt
with open("total_data.json", "r", encoding="utf-8") as f:
    total_data = json.load(f)


filter_words = ["всем", "очень", "спасибо", "авто"]
filter_two_words = ["отдельное спасибо", "так как", 'большое спасибо', 'первый раз', 'своего дела', '	очень доволен'
, 'огромное спасибо', 'очень доволен', 'все отлично', 'отличный салон']
filter_tree_words = []
filter_four_words = ['все четко и по', 'хочу выразить огромную благодарность']

def return_string(data):
   reviews = data.get("company_reviews", [])
   all_texts = []
   for review in reviews:
      all_texts.append(review["text"])
   full_text = " ".join(all_texts)
   words = re.findall(r"\b[\wёЁа-яА-Яa-zA-Z]+\b", full_text.lower()) #написал гпт
   return words, len(reviews)


def analyse(words):
   two_words =  [" ".join(words[i:i+2]) for i in range(len(words) - 1)]
   three_words = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]
   four_words = [" ".join(words[i:i+4]) for i in range(len(words) - 3)]

   words = [word for word in words if word not in filter_words]
   two_words = [word for word in two_words if word not in filter_two_words]
   words = [word for word in words if word not in filter_words]
   words = [word for word in words if len(word) > 3]

   one_word_table = pd.DataFrame(Counter(words).items(), columns=["Word", "Count"])
   one_word_table = one_word_table.sort_values(by="Count", ascending=False)

   two_words = [word for word in two_words if word not in filter_two_words]
   two_words = [
    phrase for phrase in two_words
    if all(len(word) > 2 for word in phrase.split())
    ]
   two_word_table = pd.DataFrame((Counter(two_words)).items(), columns=["Two words", "Count"])
   two_word_table = two_word_table.sort_values(by="Count", ascending=False)

   price_two = [word for word in two_words if "цен" in word and "центр" not in word]
   two_price_table = pd.DataFrame((Counter(price_two)).items(), columns=["Two words", "Count"])
   two_price_table = two_price_table.sort_values(by="Count", ascending=False)


   three_word_table = pd.DataFrame((Counter(three_words)).items(), columns=["Three words", "Count"])
   three_word_table = three_word_table.sort_values(by="Count", ascending=False)


   four_word_table = pd.DataFrame((Counter(four_words)).items(), columns=["Four words", "Count"])
   four_word_table = four_word_table.sort_values(by="Count", ascending=False)
   price_count = (
       sum(
    count
    for word, count in Counter(words).items()
    if "цен" in word and "центр" not in word
   )
   )



   return two_price_table, four_word_table, price_count

number_of_comments = 0

total_words = []
for dealer_reviews in total_data:
   dealer_wordss, dealer_counts = return_string(dealer_reviews)
   total_words = total_words + dealer_wordss
   number_of_comments = number_of_comments + dealer_counts

two_price_table, data, price_count = analyse(total_words)


print(f"Было проанализировано {number_of_comments} отзывов на {len(total_data)} дилерских центров. Упоминание цены было в {price_count} из них.")

data.columns = ["Фраза", "Количество упоминаний"]
bar_chart = px.bar((data.head(20)), x="Фраза", y="Количество упоминаний")
bar_chart.show()

two_price_table.columns = ["Фраза с упоминанием цены", "Количество упоминаний"]
bar_chartt = px.bar((two_price_table.head(20)), x="Фраза с упоминанием цены", y="Количество упоминаний")
bar_chartt.show()

my_comment = "Не смотря на то, что анализ фраз не показал важность цены для покупателей, " \
"практически каждый пятой её упоминал. Видимо это связано с ценой автомобилей. Не смотря" \
"то, что покупатели машин BMW зачастую имеют хороший доход, цена для них тем не менее играет" \
"роль. Помимо этого клиенты ценят скорость, пунктуальность, качество обслуживания, внимательное" \
"отношение к клиентам и вежливость всего персонала."
