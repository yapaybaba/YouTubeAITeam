#!/usr/bin/env python3
"""
ingest: Git diff → Wiki otomatik güncelleme CLI aracı.

Kullanım:
    python ingest.py                        # HEAD~1 karşılaştırması
    python ingest.py --since HEAD~3         # Son 3 commit
    python ingest.py --since abc123         # Belirli commit'ten bu yana
    python ingest.py --dry-run              # Neyin değişeceğini göster, yazma
    python ingest.py --model llama3.2       # Farklı Ollama modeli kullan
"""

import subprocess
import sys
from pathlib import Path
from datetime import date

import click
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.table import Table

console = Console()

# Değişen dosya → Wiki sayfası eşleştirmesi
# Yeni .py dosyası eklenirse otomatik PascalCase sayfa oluşturulur
MODULE_WIKI_MAP = {
    "agents.py": "Agents.md",
    "main.py": "Pipeline.md",
    "state.py": "AgentState.md",
    "output.py": "OutputLayer.md",
    "requirements.txt": "Dependencies.md",
}

WIKI_SCHEMA_PROMPT = """
Sen bir teknik wiki yazarısın. Türkçe yazıyorsun (teknik terimler İngilizce kalabilir).

ZORUNLU BAŞLIK FORMATI (her sayfanın en üstünde olmalı):
**Özet:** [Modülün ne yaptığını anlatan max 3 cümle]
**Kütüphaneler/Teknolojiler:** [Kullanılan kütüphaneler]
**Bağlantılar:** [[İlgiliSayfa1]], [[İlgiliSayfa2]]

KURALLAR:
- Yeni kavram/sınıf için [[Obsidian linki]] kullan
- Değişiklikleri [GÜNCELLEME: {today}] tag'i ile işaretle
- Kod örneklerini ```python bloklarına al
- Mevcut sayfa varsa sadece değişen kısmı güncelle, gerisini koru
- Spekülatif bilgi ekleme — sadece diff'ten gözlemlenebileni yaz
"""


def run_git(args: list, cwd: Path) -> str:
    result = subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True
    )
    return result.stdout.strip()


def get_file_diff(file: str, since: str, repo: Path) -> str:
    return run_git(["diff", since, "--", file], cwd=repo)


def get_current_content(file: str, repo: Path) -> str:
    path = repo / file
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def derive_wiki_name(filename: str) -> str | None:
    """Bilinmeyen .py dosyaları için PascalCase wiki adı türet."""
    if not filename.endswith(".py"):
        return None
    stem = filename.replace(".py", "")
    return "".join(word.capitalize() for word in stem.split("_")) + ".md"


def update_index(wiki_path: Path, new_pages: list[tuple[str, str]]) -> None:
    """Index.md'ye yeni sayfaların linkini ekle (Proje Bileşenleri altına)."""
    index = wiki_path / "Index.md"
    if not index.exists():
        return
    content = index.read_text(encoding="utf-8")
    for page_name, summary in new_pages:
        link = f"- [[{page_name.replace('.md', '')}]] — {summary}"
        if page_name.replace(".md", "") not in content:
            content = content.replace(
                "## Proje Bileşenleri",
                f"## Proje Bileşenleri\n{link}"
            )
    index.write_text(content, encoding="utf-8")


@click.command()
@click.option("--repo", default=".", show_default=True, help="Git repo kök dizini")
@click.option("--wiki", default="docs/wiki", show_default=True, help="Wiki dizini (repo'ya göre)")
@click.option("--since", default="HEAD~1", show_default=True, help="Diff başlangıç commit'i")
@click.option("--model", default="gemma4:e4b", show_default=True, help="Ollama modeli")
@click.option("--dry-run", is_flag=True, help="Değişiklikleri yaz, dosyaya kaydetme")
def cli(repo: str, wiki: str, since: str, model: str, dry_run: bool) -> None:
    """Git diff → Wiki sayfalarını otomatik güncelle."""

    repo_path = Path(repo).resolve()
    wiki_path = repo_path / wiki
    today = date.today().isoformat()

    console.print(f"\n[bold cyan]INGEST[/bold cyan] — {repo_path.name} @ {since}")
    if dry_run:
        console.print("[yellow]DRY RUN — dosyalara yazılmayacak[/yellow]")

    # 1. Değişen dosyaları al
    changed = run_git(["diff", since, "--name-only"], cwd=repo_path).splitlines()
    changed = [f.strip() for f in changed if f.strip()]

    if not changed:
        console.print("[dim]Değişen dosya yok.[/dim]")
        return

    console.print(f"[dim]{len(changed)} değişen dosya bulundu[/dim]")

    # 2. LLM başlat
    llm = ChatOllama(model=model, temperature=0.1)

    processed, skipped, new_pages = [], [], []

    for file in changed:
        filename = Path(file).name

        # Wiki dosyalarını atla
        if file.startswith("docs/wiki/") or file.startswith("docs/skills/"):
            skipped.append((file, "wiki/skill dosyası"))
            continue

        # Wiki sayfası belirle
        wiki_page = MODULE_WIKI_MAP.get(filename) or derive_wiki_name(filename)
        if not wiki_page:
            skipped.append((file, "eşleşme yok"))
            continue

        wiki_file = wiki_path / wiki_page
        is_new = not wiki_file.exists()
        existing = wiki_file.read_text(encoding="utf-8") if not is_new else ""

        file_diff = get_file_diff(file, since, repo_path)
        current_content = get_current_content(file, repo_path)

        action = "Oluşturuluyor" if is_new else "Güncelleniyor"
        console.print(f"\n[bold]{action}:[/bold] {wiki_page} ← [dim]{file}[/dim]")

        prompt = f"""{WIKI_SCHEMA_PROMPT.format(today=today)}

DEĞİŞEN DOSYA: {file}

GIT DIFF:
```
{file_diff[:4000]}
```

GÜNCEL DOSYA İÇERİĞİ:
```python
{current_content[:2000]}
```

{"MEVCUT WIKI SAYFASI:" if existing else "GÖREV: Yeni wiki sayfası oluştur."}
{existing[:2000] if existing else ""}

{"GÖREV: Yukarıdaki sayfayı güncelle. Yeni/değişen kısımları [GÜNCELLEME: " + today + "] tag'i ile işaretle. Değişmeyen içeriği koru." if existing else ""}

Sadece wiki sayfasının markdown içeriğini yaz. Başka açıklama ekleme."""

        if dry_run:
            console.print(f"  [dim]→ {wiki_page} (yazılmadı)[/dim]")
            processed.append((file, wiki_page, action))
            continue

        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        wiki_file.write_text(content, encoding="utf-8")

        if is_new:
            first_line = content.split("\n")[0].replace("**Özet:**", "").strip()
            new_pages.append((wiki_page, first_line[:80]))

        processed.append((file, wiki_page, action))

    # 3. Index.md güncelle
    if not dry_run and new_pages:
        update_index(wiki_path, new_pages)
        console.print(f"\n[dim]Index.md güncellendi: {len(new_pages)} yeni sayfa eklendi[/dim]")

    # 4. Rapor
    console.print()
    table = Table(show_header=True, header_style="bold")
    table.add_column("Durum")
    table.add_column("Kaynak")
    table.add_column("Wiki Sayfası")

    for file, page, action in processed:
        icon = "✅" if not dry_run else "🔍"
        table.add_row(f"{icon} {action}", file, page)
    for file, reason in skipped:
        table.add_row("⏭️  Atlandı", file, reason)

    console.print(table)


if __name__ == "__main__":
    cli()
