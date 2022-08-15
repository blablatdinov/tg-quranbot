# Схема базы данных

```mermaid
classDiagram
    files <|-- ayats
    files <|-- podcasts
    users <|-- users
    ayats <|-- suras
    cities <|-- users
    users <|-- prayers_at_user
    prayers_at_user_groups <|-- prayers_at_user
    cities <|-- prayers
    prayer_days <|-- prayers
    class ayats{
        int ayat_id
        uuid public_id
        int day
        int sura_id
        varchar ayat_number
        varchar content
        varchar arab_text
        varchar transliteration
        uuid audio_id
        uuid one_day_content_id
    }
    class suras{
        int sura_id
        varchar link
    }
    class files{
        uuid file_id
        varchar telegram_file_id
        datetime created_at
    }
    class users{
        bigint chat_id
        bool is_active
        varchar comment
        int day
        uuid city_id
        bigint referrer_id
    }
    class cities{
        uuid city_id
        varchar name
    }
    class podcasts{
        uuid podcast_id
        uuid file_id
    }
    class prayers{
        uuid id
        time time
        varchar name
        int city_id
        int day_id
    }
    class prayers_at_user{
        uuid id
        int user_id
        int prayer_id
        uuid prayer_group_id
        bool is_read
    }
    class prayers_at_user_groups{
        uuid id
    }
    class prayer_days{
        date date
    }
```
