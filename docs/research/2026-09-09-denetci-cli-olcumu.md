# Denetçi/sentez CLI ölçümü — Plan 2 Task 10 Step 3a

**Tarih:** 2026-09-09 · **Ölçen:** Task 10 yürütücüsü · **Makine:** bu VPS (linux 6.8.0-137)

`auditors.ToolSpec` eşlemesindeki argümanlar bu dosyadaki ham çıktıdan doldurulmuştur.
Uydurulmuş bayrak YOKTUR; bir bayrak burada geçmiyorsa `ToolSpec`'e GİRMEZ
(İlke 9 — ölçülmemiş değer yazılmaz).

Tekrar ölçüm kapısı: `tests/test_auditor_orchestration.py::
test_toolspec_flags_exist_in_the_installed_cli_help` her koşumda kurulu CLI'nın
yardım çıktısını yeniden okur; bayrak kaybolursa test DÜŞER.

## 1. Sürümler (ölçüm)

```
### komut: claude --version
2.1.266 (Claude Code)

### komut: codex --version
codex-cli 0.151.0
```

## 2. Ölçülen ve DONDURULAN komut satırları

| araç | argv | istem (prompt) nasıl gider |
|---|---|---|
| `denetci-1` | `claude -p --output-format text` | STDIN |
| `denetci-2` | `codex exec --skip-git-repo-check --sandbox read-only --color never -` | STDIN (`-`) |
| `sentez` | `claude -p --output-format text` | STDIN |

**İstem argv'ye GÖMÜLMEZ, STDIN'den gider.** Gerekçe ölçülmüştür: tek argümanın
bayt sınırı vardır (`ARG_MAX`), paket görev metni ise ekleriyle birlikte büyür.
`claude` için `-p` yardımı "useful for pipes" der; `codex exec` için `[PROMPT]`
yardımı "If not provided as an argument (or if `-` is used), instructions are
read from stdin" der (aşağıda ham çıktı).

**Çalışma dizini bayrakla DEĞİL alt süreç `cwd`'siyle verilir.** `claude`'ın
çalışma dizini bayrağı yoktur (yardım çıktısında `--add-dir` var, `--cd` YOK);
`codex exec`'te `-C/--cd` vardır ama iki araç için TEK mekanizma kullanmak
K-79'u tek yerde tutar — `SubprocessRunner` `subprocess.run(..., cwd=...)`
çağırır ve her rol kendi `PacketRef.kopyalar[rol]` dizininde koşar.

### `sentez` neden Claude Code — ÖLÇÜM, tercih değil

Pinlenmiş `hakem-sentez-gorevi.md` (pin sha `c201e295b776…`, doğrulandı) 4. satır:

```
Kullanım: İki denetçi çıktısı hazır olduktan sonra Claude Code'da koşulur.
```

Denetçi rollerinin araç eşlemesi (`denetci-1` → Claude Code, `denetci-2` →
Codex) planın 1267. satırında BAĞLIDIR; bu dosya onu yeniden seçmez.

## 3. ÖLÇÜLMÜŞ EKSİKLER — dürüst etiket

### (a) `codex exec` sürüm 0.151.0'da `--search` YOKTUR

Üst düzey `codex --help` `--search` ("Enable live web search") bayrağını
listeler; `codex exec --help` **listelemez** (bkz. §5 tam seçenek dökümü).
İlk yazımda argv'ye `--search` konmuştu ve yukarıdaki tekrar-ölçüm kapısı bunu
YAKALADI — bayrak `ToolSpec`'ten ÇIKARILDI.

**Sonuç (çözülmedi, dürüst etiket):** bu argv ile `denetci-2`'nin canlı web
araması AÇILMAZ. `-c features.web_search=true` biçiminde bir yapılandırma
anahtarı ölçülmedi; ölçülmemiş anahtar YAZILMAZ. Kapının kendisi zaten
fail-closed'dır: K-14 `preflight` erişimi ÖLÇER ve erişim yoksa tur BAŞLAMAZ;
sözleşmenin `URL doğrulaması yapılamadı (ortam kısıtı)` kaçışı da bu hâli
karşılar. **Evi:** Task 11 (CLI katmanı `preflight` probunu sağlayan yerdir).

### (b) Uçtan uca koşum DOĞRULANMADI

Bayrakların KABUL edildiği yardım çıktısından ölçüldü; gerçek bir model
çağrısıyla (ücretli jeton harcayan koşum) **denenmedi**. Dolayısıyla "bu argv
ile denetçi raporu üretilir" iddiası bu dosyada YAPILMAZ — ölçülen, bayrakların
kurulu sürümde var olduğudur.

### (c) İzin/sanal alan asimetrisi

`codex exec` için `--sandbox read-only` ölçüldü ve konuldu (paket kopyası
bayt-özdeş kalmalı — K-79). `claude` tarafında eşdeğer bir salt-okunur bayrak
YOK: `--restricted` komut çalıştıran araçları VE `WebFetch`'i kaldırır, yani
denetçinin URL örneklemini de öldürür. Bu asimetri BEYAN edilir, sessizce
geçilmez.

### (d) Zaman aşımı davranışı

Zaman aşımı CLI bayrağıyla DEĞİL, dış katmanda `subprocess.run(timeout=...)`
ile uygulanır — her iki CLI'nın yardımında koşum süresi sınırlayan bir bayrak
YOKTUR (§5 döküm). Davranış gerçek alt süreçle ölçülür:
`test_runner_timeout_yields_typed_timeout_outcome` 0.5 s zaman aşımına karşı
30 s uyuyan bir süreç koşar ve `durum="zaman-asimi"` · `exit_code=None`
bekler. `SubprocessRunner`'ın zaman aşımı VARSAYILANI YOKTUR (zorunlu
parametre): ölçülmemiş bir saniye değeri sabit olarak yazılmaz.

## 4. Ham çıktı — `claude --help` (ilgili satırlar)

```
Usage: claude [options] [command] [prompt]

Claude Code - starts an interactive session by default, use -p/--print for
non-interactive output

Arguments:
  prompt                                Your prompt

  --output-format <format>              Output format (only works with --print):
                                        "text" (default), "json" (single
                                        result), or "stream-json" (realtime
                                        streaming) (choices: "text", "json",
                                        "stream-json")
  --permission-mode <mode>              Permission mode to use for the session
                                        (choices: "acceptEdits", "auto",
  -p, --print                           Print response and exit (useful for
                                        pipes). Note: The workspace trust dialog
                                        is skipped when Claude is run in
                                        non-interactive mode (via -p, or when
                                        stdout is not a TTY, e.g. piped or
                                        redirected output). Only use this in
                                        directories you trust. Settings files
                                        that fail validation are silently
                                        ignored in this mode (no error dialog is
                                        shown).
  --prompt-suggestions [value]          Enable prompt suggestions. In print/SDK
                                        mode, emits a prompt_suggestion message
```

Tam çıktı 302 satırdır; yukarıdaki blok `-p/--print` ve `--output-format`
maddelerinin birebir kopyasıdır. Çalışma dizini bayrağı taraması:

```
$ claude --help | grep -cE "^\s+--cd|^\s+-C,"
0
```

## 5. Ham çıktı — `codex exec --help`

```
Run Codex non-interactively

Usage: codex exec [OPTIONS] [PROMPT]
       codex exec [OPTIONS] <COMMAND> [ARGS]

Commands:
  resume  Resume a previous session by id or pick the most recent with --last
  fork    Fork a previous session by id into a new session
  review  Run a code review against the current repository
  help    Print this message or the help of the given subcommand(s)

Arguments:
  [PROMPT]
          Initial instructions for the agent. If not provided as an argument (or if `-` is used),
          instructions are read from stdin. If stdin is piped and a prompt is also provided, stdin
          is appended as a `<stdin>` block

Options:
  -c, --config <key=value>
          Override a configuration value that would otherwise be loaded from `~/.codex/config.toml`.
          Use a dotted path (`foo.bar.baz`) to override nested values. The `value` portion is parsed
          as TOML. If it fails to parse as TOML, the raw string is used as a literal.
          
          Examples: - `-c model="o3"` - `-c 'sandbox_permissions=["disk-full-read-access"]'` - `-c
          shell_environment_policy.inherit=all`

      --enable <FEATURE>
          Enable a feature (repeatable). Equivalent to `-c features.<name>=true`

      --disable <FEATURE>
          Disable a feature (repeatable). Equivalent to `-c features.<name>=false`

      --strict-config
          Error out when config.toml contains fields that are not recognized by this version of
          Codex

  -i, --image <FILE>...
          Optional image(s) to attach to the initial prompt

  -m, --model <MODEL>
          Model the agent should use

      --oss
          Use open-source provider

      --local-provider <OSS_PROVIDER>
          Specify which local provider to use (lmstudio or ollama). If not specified with --oss,
          will use config default or show selection

  -p, --profile <CONFIG_PROFILE_V2>
          Layer $CODEX_HOME/<name>.config.toml on top of the base user config

  -s, --sandbox <SANDBOX_MODE>
          Select the sandbox policy to use when executing model-generated shell commands
          
          [possible values: read-only, workspace-write, danger-full-access]

      --approve-for-me
          Route approval requests through automatic review using the workspace-write sandbox

      --dangerously-bypass-approvals-and-sandbox
          Skip all confirmation prompts and execute commands without sandboxing. EXTREMELY
          DANGEROUS. Intended solely for running in environments that are externally sandboxed

      --dangerously-bypass-hook-trust
          Run enabled hooks without requiring persisted hook trust for this invocation. DANGEROUS.
          Intended only for automation that already vets hook sources

  -C, --cd <DIR>
          Tell the agent to use the specified directory as its working root

      --add-dir <DIR>
          Additional directories that should be writable alongside the primary workspace

      --thread-source <SOURCE>
          Source classification for newly created or forked threads

      --skip-git-repo-check
          Allow running Codex outside a Git repository

      --ephemeral
          Run without persisting session files to disk

      --ignore-user-config
          Do not load `$CODEX_HOME/config.toml`; auth still uses `CODEX_HOME`

      --ignore-rules
          Do not load user or project execpolicy `.rules` files

      --output-schema <FILE>
          Path to a JSON Schema file describing the model's final response shape

      --color <COLOR>
          Specifies color settings for use in the output
          
          [default: auto]
          [possible values: always, never, auto]

      --json
          Print events to stdout as JSONL

  -o, --output-last-message <FILE>
          Specifies file where the last message from the agent should be written

  -h, --help
          Print help (see a summary with '-h')

  -V, --version
          Print version
```

## 6. `codex exec` seçenek adlarının tam dökümü (ölçüm)

```
$ codex exec --help | grep -oE "^\s+(-[a-zA-Z], )?--[a-z-]+" | tr -d ' ' | sort -u
--add-dir
--approve-for-me
-C,--cd
-c,--config
--color
--dangerously-bypass-approvals-and-sandbox
--dangerously-bypass-hook-trust
--disable
--enable
--ephemeral
-h,--help
--ignore-rules
--ignore-user-config
-i,--image
--json
--local-provider
-m,--model
-o,--output-last-message
--oss
--output-schema
-p,--profile
--skip-git-repo-check
-s,--sandbox
--strict-config
--thread-source
-V,--version
```

`--search` bu listede YOKTUR — §3(a)'nın kanıtı budur.
