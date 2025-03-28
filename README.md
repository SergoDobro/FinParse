# GetCarz

## Состав группы
- Максим Щербаков (github: maxim1eth)
- Амир Салихов (github: SHR1Eks)
- Сергей Сухинов (github: Sergo Dobro)

## Идея компании
В условиях санкций приобрести BMW, машину мечты для многих, стало намного сложнее. GetCarz - площадка для поиска лучших предложений по автомобилям BMW, которая найдет лучшие возможности для покупки на международном авторынке. Платформа автоматически рассчитывает цену для потребителя с учетом пошлин, налогов и комиссий. При этом на GetCarz выставляются только высокомаржинальные для сервиса позиции. 

## Как это работает?
- Анализ данных Российских и иностранных автомаркетплейсов и аукционов для продажи машин. 
- Цены отслеживаются в реальном времени и передаются пользователям.   
- Учет данных о пошлинах, комиссиях и логистике

## Разделение обязанностей
- Максим Щербаков —  анализ российского рынка (авто.ру, Дром, Авито) и построение графиков.
- Амир Салихов —  анализ европейского рынка (autoscout), работа с картой дилеров-конкурентов в Москве, парсинг комментариев.
- Сергей Сухинов (тимлид) —  анализ рынка ОАЭ (DubiCars), Структуризация кода и собранных данных через api google sheets, создание аналитического дэшборда на основе собранной командой информации. 

## Как собирать данные?
- Парсинг основных параметров автомобилей с автомаркетплейсов через API, Selenium, requests
- Парсинг Яндекс карт для иследования рынка автодилеров BMW в Москве 
- Парсинг отзывов с Яндекс карт и их обработка

## Кому это нужно?
- Автолюбителям
- Автодилерам и автопереукупам, которые хотят видит картину рынка
- Тем, кто недоволен ценами на авто (всем)
- Для тех, кто не хочет переплачивать за услуги посредников и подборщиков
