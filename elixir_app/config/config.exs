import Config

# Конфигурация приложения
config :quran_bot,
  telegram_token: System.get_env("TELEGRAM_TOKEN"),
  daily_ayats: System.get_env("DAILY_AYATS", "on"),
  daily_prayers: System.get_env("DAILY_PRAYERS", "on"),
  ramadan_mode: System.get_env("RAMADAN_MODE", "false") == "true",
  admin_chat_ids: [],
  database_url: System.get_env("DATABASE_URL", "postgresql://postgres:postgres@localhost/quranbot"),
  redis_url: System.get_env("REDIS_URL", "redis://localhost:6379"),
  webhook_port: String.to_integer(System.get_env("WEBHOOK_PORT") || "4000"),
  webhook_secret: System.get_env("WEBHOOK_SECRET")

# Конфигурация базы данных
config :quran_bot, QuranBot.Repo,
  url: System.get_env("DATABASE_URL", "postgresql://postgres:postgres@localhost/quranbot"),
  pool_size: String.to_integer(System.get_env("POOL_SIZE") || "10")

# Конфигурация логгера
config :logger,
  level: String.to_atom(System.get_env("LOG_LEVEL") || "info"),
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

# Конфигурация HTTP клиента
config :httpoison,
  timeout: 30_000,
  recv_timeout: 30_000

# Конфигурация для разработки
if config_env() == :dev do
  config :logger,
    level: :debug,
    compile_time_purge_matching: [
      [level_lower_than: :info]
    ]
end

# Конфигурация для тестов
if config_env() == :test do
  config :quran_bot, QuranBot.Repo,
    url: "postgresql://postgres:postgres@localhost/quranbot_test",
    pool: Ecto.Adapters.SQL.Sandbox

  config :logger,
    level: :warn
end
