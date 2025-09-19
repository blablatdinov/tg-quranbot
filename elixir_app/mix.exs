defmodule QuranBot.MixProject do
  use Mix.Project

  def project do
    [
      app: :quran_bot,
      version: "0.1.0",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      elixirc_paths: elixirc_paths(Mix.env())
    ]
  end

  def application do
    [
      extra_applications: [:logger, :runtime_tools],
      mod: {QuranBot.Application, []}
    ]
  end

  defp deps do
    [
      {:ecto_sql, "~> 3.10"},
      {:postgrex, ">= 0.0.0"},
      {:jason, "~> 1.4"},
      {:httpoison, "~> 2.0"},
      {:redix, "~> 0.12"},
      {:plug_cowboy, "~> 2.6"},
      {:plug, "~> 1.14"},
      {:timex, "~> 3.7"},
      {:prometheus_ex, "~> 3.0"},
      {:prometheus_plugs, "~> 1.1"},
      {:prometheus_phoenix, "~> 1.3"},
      {:prometheus_ecto, "~> 1.4"},
      {:prometheus_process_collector, "~> 1.4"},
      {:sentry, "~> 10.0"},
      {:credo, "~> 1.7", only: [:dev, :test], runtime: false},
      {:dialyxir, "~> 1.4", only: [:dev, :test], runtime: false}
    ]
  end

  defp elixirc_paths(:test), do: ["lib", "test/support"]
  defp elixirc_paths(_), do: ["lib"]
end
