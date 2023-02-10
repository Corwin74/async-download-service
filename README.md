# Микросервис для скачивания файлов

Микросервис помогает работе основного сайта, сделанного на CMS и обслуживает
запросы на скачивание архивов с файлами. Микросервис не умеет ничего, кроме упаковки файлов
в архив. Закачиваются файлы на сервер через FTP или админку CMS.

Создание архива происходит на лету по запросу от пользователя. Архив не сохраняется на диске, вместо этого по мере упаковки он сразу отправляется пользователю на скачивание.

От неавторизованного доступа архив защищен хешом в адресе ссылки на скачивание, например: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. Хеш задается названием каталога с файлами, выглядит структура каталога так:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```


## Как установить

Для работы микросервиса нужен Python версии не ниже 3.6 и архиватор zip.

```bash
pip install -r requirements.txt
```

## Как запустить

```bash
python server.py
```

Сервер запустится на порту 8080, чтобы проверить его работу перейдите в браузере на страницу [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

Доступны следюущие аргументы при запуске из командной строки:
-  -d или -directory   
  Позволяет задать каталог, в котором микросервис будет искать подкаталоги с именами хешей. По умолчанию микросервис ищет в подкаталоге `photos/` относительно папки, где находится файл `server.py`. Можно задать в виде аболютного пути (начинающегося с '\'), например:  
  ```bash
  python server.py -d /home/photo_service/photos/
  ```  
  либо относитеьного:
  ```bash
   python server.py -d photos
```  
-  `-l` или `--latency`  
 Задает задержку между циклами чтения и отправки данных микросервисом. По умолчанию задержка равна 1 секунде. При нулевом значении возможно ошибки при передаче данных.  
 - -v или --verbose  
  Включает режим отладки, сервис в процессе работы выводит дополнительную информацию.  
  
## Как развернуть на сервере

```bash
python server.py
```

После этого перенаправить на микросервис запросы, начинающиеся с `/archive/`. Например:  


```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```

# Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).